import time
import logging
import threading
import paramiko
import numpy as np

logger = logging.getLogger('honeypot_session')

class Session:
    """Handles SSH session interaction and command processing"""
    
    def __init__(self, client_ip, agent):
        self.client_ip = client_ip
        self.agent = agent
        self.start_time = time.time()
        self.command_count = 0
        self.command_history = []
        
        # Fake environment responses
        self.responses = {
            'pwd': '/home/admin',
            'whoami': 'root',
            'ls': 'config.yaml\ndata.db\nsecrets.txt',
            'id': 'uid=0(root) gid=0(root) groups=0(root)',
            'uname -a': 'Linux honeypot 5.10.0-8-amd64 #1 SMP Debian 5.10.46-5 (2021-09-23) x86_64 GNU/Linux',
            'cat /etc/passwd': 'root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash',
        }
        
        # Notify UI of new connection
        self._notify_ui('connection', {'ip': client_ip})
        logger.info(f"New session from {client_ip}")
    
    def handle_session(self, channel):
        """Main session handler"""
        channel.send(b"Welcome to Ubuntu 20.04.3 LTS\r\n")
        channel.send(b"server:~$ ")
        
        buffer = b''
        
        while True:
            try:
                data = channel.recv(1024)
                if not data:
                    break
                
                # Echo input
                channel.send(data)
                
                buffer += data
                
                # Process if enter key pressed
                if b'\r' in buffer:
                    command = buffer.split(b'\r')[0].decode('utf-8', errors='ignore').strip()
                    buffer = b''
                    
                    if command:
                        self._process_command(command, channel)
                        channel.send(b"server:~$ ")
            
            except Exception as e:
                logger.error(f"Error in session: {e}")
                break
        
        duration = time.time() - self.start_time
        logger.info(f"Session from {self.client_ip} closed after {duration:.2f}s with {self.command_count} commands")
    
    def _process_command(self, command, channel):
        """Process a command using RL agent"""
        self.command_count += 1
        self.command_history.append(command)
        
        # Extract features for RL state
        features = self._extract_features(command)
        
        # Notify UI of command
        self._notify_ui('command', {
            'command': command,
            'ip': self.client_ip,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Get action from RL agent
        action = self.agent.decide_action(features)
        
        # Execute action
        response = self._execute_action(action, command, channel)
        
        # Calculate reward
        reward = self.agent.calculate_reward(command, action)
        
        # Update RL model
        self.agent.update(features, action, reward)
        
        # Notify UI of action
        self._notify_ui('action', {
            'command': command,
            'action': action,
            'reward': reward,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        logger.info(f"Command '{command}' from {self.client_ip} -> Action: {action}, Reward: {reward:.2f}")
        
        return response
    
    def _extract_features(self, command):
        """Extract features from command for RL state"""
        return np.array([
            int('wget' in command),
            int('curl' in command),
            int('./' in command),
            int('sudo' in command),
            int('rm' in command),
            int('chmod' in command),
            len(command)
        ], dtype=np.float32)
    
    def _execute_action(self, action, command, channel):
        """Execute the chosen action"""
        cmd_base = command.split()[0] if command.split() else ""
        
        if action == 'allow':
            # Generate response for allowed command
            response = self.responses.get(command, f"Command '{cmd_base}' executed successfully.")
            channel.send(f"\r\n{response}\r\n".encode())
            
        elif action == 'block':
            channel.send(b"\r\nPermission denied.\r\n")
            
        elif action == 'substitute':
            fake_response = self._generate_fake_response(command)
            channel.send(f"\r\n{fake_response}\r\n".encode())
            
        elif action == 'delay':
            # Simulate processing delay
            time.sleep(2)
            channel.send(b"\r\nCommand processed after delay.\r\n")
            
        elif action == 'insult':
            insults = [
                "Nice try, skiddie!",
                "You thought that would work? Cute.",
                "Hacking attempt detected. IP logged.",
                "Your hacking skills need work.",
                "Command blocked. Try harder."
            ]
            channel.send(f"\r\n{np.random.choice(insults)}\r\n".encode())
        
        return action
    
    def _generate_fake_response(self, command):
        """Generate fake response for substitution action"""
        cmd_base = command.split()[0] if command.split() else ""
        
        fake_responses = {
            'ls': "file1.txt  file2.log  totally-not-a-honeypot.conf",
            'cat': "Error: file not found or permission denied",
            'wget': "Connecting to server... Failed: Network unreachable",
            'curl': "curl: (7) Failed to connect to port 80: Connection refused",
            'id': "uid=1000(user) gid=1000(user) groups=1000(user)",
            'whoami': "user",
            'pwd': "/home/user"
        }
        
        return fake_responses.get(cmd_base, f"Command '{cmd_base}' executed with unexpected result.")
    
    def _notify_ui(self, event_type, data):
        """Notify UI components of events"""
        
        from main import ui_components
        
        for ui in ui_components:
            try:
                ui.update(event_type, data)
            except Exception as e:
                logger.error(f"Error updating UI: {e}")