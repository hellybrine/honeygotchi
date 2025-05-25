import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading
import random
import time
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from faces import show_face
from banner import generate_banner
from rl_agent import EnhancedRLAgent
from deception_engine import AdaptiveDeceptionEngine

# Enhanced logging setup (keeping your existing format)
logging_format = logging.Formatter('%(asctime)s - %(message)s')
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('logs/audits.log', maxBytes=5000000, backupCount=10)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('logs/cmd_audits.log', maxBytes=5000000, backupCount=10)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

class EnhancedSessionTracker:
    """Enhanced version of your existing session tracker"""
    
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.session_data = {
            'start_time': time.time(),
            'commands': [],
            'command_times': [],
            'commands_count': 0,
            'unique_commands': 0,
            'file_access_attempts': 0,
            'malware_downloads': 0,
            'privilege_escalation_attempts': 0,
            'network_scan_attempts': 0,
            'persistence_attempts': 0,
            'data_exfiltration_attempts': 0,
            'failed_commands': 0,
            'suspicious_patterns': 0,
            'avg_time_between_commands': 0,
            'command_complexity_score': 0,
            'repeat_command_ratio': 0,
            'current_engagement_level': 1,
            'session_duration': 0,
            'attacker_type': 'beginner',
            'discovered_files': [],
            'deception_triggered': 0,
            'intelligence_value': 0
        }

    def update_session(self, command):
        current_time = time.time()
        self.session_data['commands'].append(command)
        self.session_data['command_times'].append(current_time)
        self.session_data['commands_count'] += 1
        self.session_data['session_duration'] = current_time - self.session_data['start_time']
        
        # Update metrics (keeping your existing logic)
        self._update_metrics(command)

    def _update_metrics(self, command):
        cmd_lower = command.lower()
        
        # Update unique commands
        self.session_data['unique_commands'] = len(set(self.session_data['commands']))
        
        # Update specific counters (your existing patterns)
        if any(pattern in cmd_lower for pattern in ['cat', 'less', 'more', 'head', 'tail', 'vim', 'nano']):
            self.session_data['file_access_attempts'] += 1
        
        if any(pattern in cmd_lower for pattern in ['wget', 'curl', 'download', 'git clone']):
            self.session_data['malware_downloads'] += 1
        
        if any(pattern in cmd_lower for pattern in ['sudo', 'su', 'chmod', 'chown', 'passwd']):
            self.session_data['privilege_escalation_attempts'] += 1
        
        if any(pattern in cmd_lower for pattern in ['nmap', 'netstat', 'ss', 'lsof', 'nslookup']):
            self.session_data['network_scan_attempts'] += 1
        
        if any(pattern in cmd_lower for pattern in ['crontab', 'systemctl', 'service', 'rc.local']):
            self.session_data['persistence_attempts'] += 1
        
        if any(pattern in cmd_lower for pattern in ['scp', 'rsync', 'tar', 'zip', 'base64']):
            self.session_data['data_exfiltration_attempts'] += 1

        # Calculate time intervals
        if len(self.session_data['command_times']) > 1:
            intervals = [self.session_data['command_times'][i] - self.session_data['command_times'][i-1]
                        for i in range(1, len(self.session_data['command_times']))]
            self.session_data['avg_time_between_commands'] = np.mean(intervals)

        # Calculate complexity score
        complexity_indicators = ['|', '&&', '||', ';', '>', '<', '`', '$', '{', '}']
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in command)
        self.session_data['command_complexity_score'] = complexity_score

        # Calculate repeat ratio
        if self.session_data['commands_count'] > 0:
            unique_count = len(set(self.session_data['commands']))
            self.session_data['repeat_command_ratio'] = 1 - (unique_count / self.session_data['commands_count'])

class ResponsePlanningEngine:
    """Enhanced version of your existing response planner"""
    
    def __init__(self):
        self.threat_levels = {
            'low': {'block_probability': 0.05, 'alert_level': 1},
            'medium': {'block_probability': 0.15, 'alert_level': 2},
            'high': {'block_probability': 0.35, 'alert_level': 3},
            'critical': {'block_probability': 0.60, 'alert_level': 4}
        }

    def assess_threat_level(self, session_data):
        threat_score = 0
        
        # Weight different factors (keeping your existing logic)
        threat_score += session_data.get('malware_downloads', 0) * 4
        threat_score += session_data.get('privilege_escalation_attempts', 0) * 3
        threat_score += session_data.get('data_exfiltration_attempts', 0) * 5
        threat_score += session_data.get('persistence_attempts', 0) * 3
        threat_score += session_data.get('network_scan_attempts', 0) * 2

        if threat_score >= 15:
            return 'critical'
        elif threat_score >= 8:
            return 'high'
        elif threat_score >= 4:
            return 'medium'
        else:
            return 'low'

    def plan_response(self, threat_level, session_data):
        threat_config = self.threat_levels[threat_level]
        
        # Calculate intelligence value
        intelligence_value = self._calculate_intelligence_value(session_data)
        
        # Adjust based on intelligence value
        if intelligence_value > 0.7:
            block_prob = threat_config['block_probability'] * 0.3
        elif intelligence_value > 0.4:
            block_prob = threat_config['block_probability'] * 0.6
        else:
            block_prob = threat_config['block_probability']

        return {
            'should_block': random.random() < block_prob,
            'alert_level': threat_config['alert_level'],
            'intelligence_value': intelligence_value,
            'recommended_engagement': self._recommend_engagement(threat_level, intelligence_value)
        }

    def _calculate_intelligence_value(self, session_data):
        score = 0
        score += min(session_data.get('unique_commands', 0) / 20, 1) * 0.3
        score += min(session_data.get('session_duration', 0) / 300, 1) * 0.2
        score += min(session_data.get('commands_count', 0) / 50, 1) * 0.2
        score += (session_data.get('command_complexity_score', 0) / 10) * 0.3
        return min(score, 1.0)

    def _recommend_engagement(self, threat_level, intelligence_value):
        if threat_level == 'critical' and intelligence_value < 0.3:
            return 0  # Eject
        elif intelligence_value > 0.7:
            return 3  # High engagement
        elif intelligence_value > 0.4:
            return 2  # Medium engagement
        else:
            return 1  # Low engagement

class DataCollector:
    """Enhanced data collection with training data export"""
    
    def __init__(self):
        self.training_data = []
        self.session_logs = []
        os.makedirs('data', exist_ok=True)

    def collect_session_data(self, session_tracker, rl_actions, reward):
        session_summary = {
            'timestamp': datetime.now().isoformat(),
            'client_ip': session_tracker.client_ip,
            'session_data': session_tracker.session_data.copy(),
            'rl_actions': rl_actions,
            'reward': reward
        }
        
        self.session_logs.append(session_summary)
        
        # Save to file periodically
        if len(self.session_logs) % 10 == 0:
            self.save_training_data()

    def save_training_data(self):
        with open('data/training_data.json', 'w') as f:
            json.dump(self.session_logs, f, indent=2)

    def export_to_csv(self):
        """Export session data to CSV for analysis"""
        if not self.session_logs:
            return
        
        # Flatten session data for CSV export
        flattened_data = []
        for session in self.session_logs:
            row = {
                'timestamp': session['timestamp'],
                'client_ip': session['client_ip'],
                'reward': session['reward'],
                **session['session_data'],
                **{f'rl_action_{k}': v for k, v in session['rl_actions'].items()}
            }
            flattened_data.append(row)
        
        df = pd.DataFrame(flattened_data)
        df.to_csv('data/honeypot_dataset.csv', index=False)
        print(f"Exported {len(df)} sessions to data/honeypot_dataset.csv")

    def load_training_data(self):
        try:
            with open('data/training_data.json', 'r') as f:
                self.session_logs = json.load(f)
        except FileNotFoundError:
            self.session_logs = []

class EnhancedHoneypotServer:
    """Enhanced version of your existing honeypot server"""
    
    def __init__(self):
        # Initialize components
        self.rl_agent = EnhancedRLAgent()
        self.deception_engine = AdaptiveDeceptionEngine()
        self.response_planner = ResponsePlanningEngine()
        self.data_collector = DataCollector()
        
        # Load existing models if available
        self.rl_agent.load_model()
        
        # Stats (keeping your existing format)
        self.stats = {
            "Logged IPs": 0,
            "Commands Captured": 0,
            "Malware Dropped": 0,
            "Attack Type": "Unknown",
            "Active Sessions": 0,
            "Intelligence Gathered": 0,
            "RL Training Episodes": 0
        }
        
        self.recent_activity = []
        self.active_sessions = {}
        
        # Load existing training data
        self.data_collector.load_training_data()
        
        # SSH Configuration (keeping your existing setup)
        self.SSH_BANNER = "SSH-2.0-OpenSSH_8.2p1"
        try:
            self.host_key = paramiko.RSAKey(filename='server.key')
        except FileNotFoundError:
            self.host_key = paramiko.RSAKey.generate(2048)
            self.host_key.write_private_key_file('server.key')

    def calculate_reward(self, session_data, rl_actions, session_duration):
        """Enhanced reward calculation"""
        reward = 0
        
        # Base reward for engagement
        reward += session_duration * 0.1
        reward += session_data.get('commands_count', 0) * 0.5
        reward += session_data.get('unique_commands', 0) * 1.0
        
        # Bonus for intelligence gathering
        reward += session_data.get('malware_downloads', 0) * 5
        reward += session_data.get('privilege_escalation_attempts', 0) * 3
        reward += session_data.get('data_exfiltration_attempts', 0) * 4
        reward += session_data.get('deception_triggered', 0) * 3
        
        # Bonus for file discovery
        reward += len(session_data.get('discovered_files', [])) * 2
        
        # Penalty for premature ejection
        if rl_actions.get('engagement', 1) == 0 and session_duration < 30:
            reward -= 10
        
        # Bonus for maintaining long sessions
        if session_duration > 300:  # 5 minutes
            reward += 20
        
        return max(reward, -10)

    def emulated_shell(self, channel, client_ip, username="unknown"):
        """Enhanced shell emulation with RL integration"""
        session_tracker = EnhancedSessionTracker(client_ip)
        self.active_sessions[client_ip] = session_tracker
        self.stats["Active Sessions"] += 1

        try:
            prompt = b'\r\nuser@honeypot:~$ '
            channel.send(prompt)
            command = b""

            while True:
                try:
                    char = channel.recv(1)
                    if not char:
                        break

                    # Handle backspace
                    if char in (b'\x7f', b'\x08'):
                        if len(command) > 0:
                            command = command[:-1]
                            channel.send(b'\b \b')
                        continue

                    # Handle Enter key
                    if char in (b'\r', b'\n'):
                        cmd_str = command.decode('utf-8', errors='ignore').strip()
                        if not cmd_str:
                            channel.send(prompt)
                            command = b""
                            continue

                        # Update session tracking
                        session_tracker.update_session(cmd_str)
                        self.stats["Commands Captured"] += 1

                        # Log command
                        creds_logger.info(f"{client_ip} > {cmd_str}")
                        self.recent_activity.append(f"{client_ip} > {cmd_str}")
                        if len(self.recent_activity) > 10:
                            self.recent_activity.pop(0)

                        # Get RL actions
                        rl_actions = self.rl_agent.select_action(session_tracker.session_data)
                        
                        # Classify attacker and assess threat
                        attacker_type = self.deception_engine.classify_attacker_skill(session_tracker.session_data)
                        session_tracker.session_data['attacker_type'] = attacker_type
                        
                        threat_level = self.response_planner.assess_threat_level(session_tracker.session_data)
                        response_plan = self.response_planner.plan_response(threat_level, session_tracker.session_data)

                        # Handle exit command
                        if cmd_str.lower() == 'exit':
                            session_duration = time.time() - session_tracker.session_data['start_time']
                            reward = self.calculate_reward(session_tracker.session_data, rl_actions, session_duration)
                            
                            # Store experience for training
                            current_state = self.rl_agent.get_state(session_tracker.session_data)
                            next_state = np.zeros_like(current_state)  # Terminal state
                            self.rl_agent.remember(current_state, rl_actions, reward, next_state, True)
                            
                            # Collect data
                            self.data_collector.collect_session_data(session_tracker, rl_actions, reward)
                            
                            channel.send(b'\r\nGoodbye!\r\n')
                            break

                        # Generate adaptive response using enhanced deception engine
                        if response_plan['should_block'] and threat_level == 'critical':
                            channel.send(b'\r\nConnection terminated due to security policy.\r\n')
                            break

                        # Use enhanced deception engine with RL actions
                        response = self.deception_engine.generate_adaptive_response(
                            cmd_str, attacker_type, rl_actions, session_tracker.session_data
                        )

                        # Handle ejection
                        if rl_actions.get('engagement', 1) == 0:
                            channel.send(b'\r\nConnection timeout\r\n')
                            break

                        channel.send(response)
                        channel.send(prompt)
                        command = b""

                        # Train the agent periodically
                        if len(self.rl_agent.memory) > 64:
                            self.rl_agent.replay()
                            self.stats["RL Training Episodes"] += 1

                        # Update stats
                        self.stats["Intelligence Gathered"] = len(self.data_collector.session_logs)
                        self.stats["Attack Type"] = f"{attacker_type.title()} - {threat_level.title()}"
                        
                        time.sleep(0.1)
                        continue

                    channel.send(char)
                    command += char

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error in shell loop: {e}")
                    break

        except Exception as e:
            print(f"Error in emulated shell: {e}")
        finally:
            self.stats["Active Sessions"] -= 1
            if client_ip in self.active_sessions:
                del self.active_sessions[client_ip]

    def client_handler(self, client, addr):
        """Enhanced client handler (keeping your existing structure)"""
        client_ip = addr[0]
        self.stats["Logged IPs"] += 1
        print(f"{client_ip} has connected to the enhanced honeypot")
        
        transport = None
        try:
            transport = paramiko.Transport(client)
            transport.local_version = self.SSH_BANNER
            server = HoneypotSSHServer(client_ip)
            transport.add_server_key(self.host_key)
            transport.start_server(server=server)
            
            channel = transport.accept(100)
            if channel is None:
                print("No channel opened.")
                return

            # Wait for authentication
            while server.session_username is None:
                time.sleep(0.01)

            # Send banner
            banner = generate_banner(username=server.session_username)
            channel.send(banner.encode())

            # Start enhanced shell emulation
            self.emulated_shell(channel, client_ip, server.session_username)

        except Exception as error:
            print(f"Error in client handler: {error}")
        finally:
            try:
                if transport:
                    transport.close()
                client.close()
            except Exception as error:
                print(f"Error while closing: {error}")

    def start_server(self, address='0.0.0.0', port=2223):
        """Start the enhanced honeypot server"""
        socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socks.bind((address, port))
        socks.listen(50)
        
        print(f"Enhanced Honeygotchi is active on port {port}")
        print("Features: PyTorch RL, Adaptive Deception, Fake Filesystem, Response Planning")
        
        # Start status display
        threading.Thread(target=self._status_display, daemon=True).start()
        
        # Start periodic model saving
        threading.Thread(target=self._periodic_save, daemon=True).start()

        while True:
            try:
                client, addr = socks.accept()
                thread = threading.Thread(target=self.client_handler, args=(client, addr))
                thread.daemon = True
                thread.start()
            except Exception as error:
                print(f"Error in honeypot listener: {error}")

    def _status_display(self):
        """Enhanced status display (keeping your existing faces)"""
        while True:
            try:
                mode = "active" if self.stats["Active Sessions"] > 0 else "sleeping"
                if self.stats["Commands Captured"] > 50:
                    mode = "happy"
                elif any("malware" in activity.lower() or "wget" in activity.lower()
                        for activity in self.recent_activity[-5:]):
                    mode = "under_attack"

                show_face(mode, self.stats, self.recent_activity, repeat=1, delay=2)
                time.sleep(5)
            except Exception as e:
                print(f"Error in status display: {e}")
                time.sleep(5)

    def _periodic_save(self):
        """Periodically save models and export data"""
        while True:
            try:
                time.sleep(300)  # Save every 5 minutes
                self.rl_agent.save_model()
                self.data_collector.export_to_csv()
                print("Models and data saved automatically")
            except Exception as e:
                print(f"Error in periodic save: {e}")

    def export_models(self):
        """Export models for production deployment"""
        self.rl_agent.export_for_production()
        print("Production models exported to models/ directory")

class HoneypotSSHServer(paramiko.ServerInterface):
    """SSH server interface (keeping your existing implementation)"""
    
    def __init__(self, client_ip):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.session_username = None

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        self.session_username = username
        funnel_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    honeypot = EnhancedHoneypotServer()
    
    try:
        honeypot.start_server('0.0.0.0', 2223)
    except KeyboardInterrupt:
        print("\nShutting down honeypot...")
        honeypot.export_models()
        honeypot.data_collector.export_to_csv()
        print("Models and data exported. Goodbye!")