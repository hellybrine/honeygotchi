import asyncio
import json
import logging
import random
import time
import uuid
from datetime import datetime
from typing import Optional

import asyncssh

from .agent import QLearningAgent, SessionTracker, classify, phase_of
from .commands import CommandProcessor
from .fakefs import FakeFileSystem
from .metrics import STATS

logger = logging.getLogger(__name__)

BANNER = (
    "Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-150-generic x86_64)\n\n"
    " * Documentation:  https://help.ubuntu.com\n"
    " * Management:     https://landscape.canonical.com\n"
    " * Support:        https://ubuntu.com/advantage\n\n"
    "Last login: {last_login} from 192.168.1.1\n"
)


async def _read_line(stdin, stdout, echo: bool) -> Optional[str]:
    """Read a line from an asyncssh stream, handling PTY raw input.

    When a PTY is attached the client sends characters one at a time and
    expects the server to echo. We also handle backspace (\x7f / \b) and
    Ctrl-C (\x03) / Ctrl-D (\x04) the way a real shell would.
    """
    buf: list[str] = []
    while True:
        try:
            ch = await stdin.read(1)
        except (asyncssh.BreakReceived, asyncssh.SignalReceived):
            continue
        except asyncssh.TerminalSizeChanged:
            continue
        except (asyncssh.ConnectionLost, ConnectionResetError):
            return None
        if not ch:
            return None
        if ch in ('\r', '\n'):
            if echo:
                stdout.write('\r\n')
            return ''.join(buf)
        if ch in ('\x7f', '\b'):
            if buf:
                buf.pop()
                if echo:
                    stdout.write('\b \b')
            continue
        if ch == '\x03':  # Ctrl-C
            if echo:
                stdout.write('^C\r\n')
            buf.clear()
            return ''
        if ch == '\x04':  # Ctrl-D
            if not buf:
                return None
            continue
        if ord(ch[0]) < 0x20 and ch not in ('\t',):
            continue
        buf.append(ch)
        if echo:
            stdout.write(ch)


class SessionRunner:
    """One SSH session: owns a FakeFileSystem + CommandProcessor and drives the
    command loop. The RL agent is shared across all sessions; this object feeds
    it decisions and reward signals."""

    def __init__(self, agent: QLearningAgent, audit_logger: logging.Logger, seed_salt: str = ''):
        self.agent = agent
        self.audit = audit_logger
        self.seed_salt = seed_salt

    async def run(self, process: asyncssh.SSHServerProcess):
        channel = process.channel
        peer = channel.get_extra_info('peername') if channel else None
        client_ip = peer[0] if peer else 'unknown'
        username = (channel.get_extra_info('username') if channel else None) or 'user'

        session_id = str(uuid.uuid4())
        session_seed = f"{self.seed_salt}:{client_ip}:{session_id}"
        hostname = f"srv-{abs(hash(session_seed)) % 9000 + 1000:04d}"
        fs = FakeFileSystem(seed=session_seed, hostname=hostname)
        processor = CommandProcessor(fs, hostname, username, rng=random.Random(session_seed))
        tracker = SessionTracker()

        has_pty = process.get_terminal_type() is not None
        stdin, stdout = process.stdin, process.stdout

        STATS.start_session(session_id, client_ip, username)
        session_start = time.time()

        self.audit.info(json.dumps({
            'event': 'session_start',
            'session_id': session_id,
            'client_ip': client_ip,
            'username': username,
            'pty': has_pty,
            'timestamp': datetime.now().isoformat(),
        }))

        last_login = datetime.now().strftime('%a %b %d %H:%M:%S %Y')
        stdout.write(BANNER.format(last_login=last_login))

        try:
            await self._loop(stdin, stdout, has_pty, processor, tracker, session_id, client_ip, username)
        except (asyncssh.ConnectionLost, ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            logger.exception("session error for %s: %s", client_ip, e)
        finally:
            if tracker.pending:
                self.agent.observe_session_end(tracker.pending, tracker.command_count)
                tracker.pending = None
            duration = time.time() - session_start
            STATS.end_session(session_id)
            self.audit.info(json.dumps({
                'event': 'session_end',
                'session_id': session_id,
                'client_ip': client_ip,
                'username': username,
                'duration_seconds': round(duration, 2),
                'command_count': tracker.command_count,
                'timestamp': datetime.now().isoformat(),
            }))
            self.agent.save_state()
            try:
                process.exit(0)
            except Exception:
                pass

    async def _loop(self, stdin, stdout, has_pty, processor, tracker, session_id, client_ip, username):
        while True:
            prompt = f"{username}@{processor.hostname}:{processor.fs.pwd()}$ "
            stdout.write(prompt)
            try:
                if has_pty:
                    line = await _read_line(stdin, stdout, echo=True)
                else:
                    line_data = await stdin.readline()
                    line = None if not line_data else line_data.rstrip('\r\n')
            except asyncssh.ConnectionLost:
                return
            if line is None:
                return
            command = line.strip()
            if not command:
                continue

            pattern = classify(command)
            is_malicious = pattern != 'none'
            next_state = f"{pattern}|{phase_of(tracker.command_count)}"

            if tracker.pending:
                self.agent.observe_next_command(tracker.pending, next_state, is_malicious)

            action, decision = self.agent.select_action(command, tracker)
            tracker.command_count += 1
            tracker.pending = decision

            self.audit.info(json.dumps({
                'event': 'command',
                'session_id': session_id,
                'client_ip': client_ip,
                'username': username,
                'command': command,
                'action': action,
                'pattern': pattern,
                'command_count': tracker.command_count,
                'timestamp': datetime.now().isoformat(),
            }))
            STATS.record_command(session_id, command, action, pattern, is_malicious)

            try:
                output = await processor.execute(command, action, {
                    'session_id': session_id,
                    'client_ip': client_ip,
                    'username': username,
                    'command_count': tracker.command_count,
                })
            except Exception as e:
                logger.exception("command error: %s", e)
                output = 'bash: internal error\n'

            if output == '__EXIT__':
                stdout.write('logout\n')
                return
            if output:
                # Ensure CRLF on PTY so output lines up properly in the client terminal.
                text = output.replace('\n', '\r\n') if has_pty else output
                stdout.write(text)
            if action == 'BLOCK':
                await asyncio.sleep(0.5)
                return


class HoneygotchiServer(asyncssh.SSHServer):
    """Auth-side: we log login attempts and *always* accept them. The
    interesting behavior is in the session loop, not the auth challenge."""

    def __init__(self, audit_logger: logging.Logger):
        self.audit = audit_logger
        self.client_ip = 'unknown'
        self.username = 'unknown'

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        peer = conn.get_extra_info('peername')
        self.client_ip = peer[0] if peer else 'unknown'
        logger.info("connection from %s", self.client_ip)

    def begin_auth(self, username: str) -> bool:
        self.username = username
        return True

    def password_auth_supported(self) -> bool:
        return True

    def public_key_auth_supported(self) -> bool:
        return True

    def validate_password(self, username: str, password: str) -> bool:
        self.username = username
        STATS.record_login(self.client_ip, username, password, accepted=True)
        self.audit.info(json.dumps({
            'event': 'auth_password',
            'client_ip': self.client_ip,
            'username': username,
            'password': password,
            'timestamp': datetime.now().isoformat(),
        }))
        return True

    def validate_public_key(self, username: str, key: asyncssh.SSHKey) -> bool:
        self.username = username
        try:
            fp = key.get_fingerprint()
        except Exception:
            fp = 'unknown'
        STATS.record_login(self.client_ip, username, f'[pubkey:{fp}]', accepted=True)
        self.audit.info(json.dumps({
            'event': 'auth_pubkey',
            'client_ip': self.client_ip,
            'username': username,
            'fingerprint': fp,
            'timestamp': datetime.now().isoformat(),
        }))
        return True


def ensure_host_key(path: str):
    """Generate an RSA host key at `path` if missing. Uses asyncssh so we
    don't need ssh-keygen on the host."""
    import os
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    key = asyncssh.generate_private_key('ssh-rsa', key_size=2048)
    key.write_private_key(path)
    logger.info("generated SSH host key at %s", path)
