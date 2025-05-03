import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading
import random
import time
from faces import show_face
from banner import generate_banner
from model import predict_attack

# Global Constant
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

logging_format = logging.Formatter('%(message)s')
host_key = paramiko.RSAKey(filename='server.key')

# Log Module
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

# Fake file generation
fake_files = [
    "important_data.txt", "top_secret.key", "flag.txt", "admin.db",
    "config_backup.tar.gz", "vulnerable_script.sh", "malicious_payload.py",
    "user_data.db", "logs/system.log", "pwned_file.txt", "security_breach.log",
    "private_key.pem", "readme.md", "license.txt", "db_backup.sql",
    "hidden/secret_config.json", "hidden/backup/compromised_backup.tar"
]

stats = {
    "Logged IPs": 0,
    "Commands Captured": 0,
    "Malware Dropped": 0,
    "Attack Type": "Unknown"
}
recent_activity = []

def generate_fake_files():
    return random.sample(fake_files, k=random.randint(5, len(fake_files)))

def fake_ls(command):
    if 'ls -a' in command or 'ls' in command:
        fake_files_list = generate_fake_files()
        response = '\n'.join(fake_files_list) + '\r\n'
        return response.encode()
    return None

def log_command(cmd: bytes, client_ip: str):
    cmd_str = cmd.strip().decode(errors='ignore')
    creds_logger.info(f"{client_ip} > {cmd_str}")
    stats["Commands Captured"] += 1
    recent_activity.append(f"{client_ip} > {cmd_str}")
    if len(recent_activity) > 10:
        recent_activity.pop(0)
    return cmd_str

def emulated_shell(channel, client_ip, failed_attempts=0):
    session_commands = []
    total_command_length = 0

    channel.send(b'prod-server3$ ')
    command = b""
    while True:
        char = channel.recv(1)
        if not char:
            channel.close()
            break
        channel.send(char)
        command += char
        if char == b'\r':
            cmd_str = log_command(command, client_ip)
            session_commands.append(cmd_str)
            total_command_length += len(cmd_str)
            # ML prediction after each command
            features = [
                len(session_commands),
                total_command_length,
                failed_attempts
            ]
            attack_type = predict_attack(features)
            stats["Attack Type"] = attack_type

            if cmd_str == 'exit':
                response = b'\n Goodbye!\n'
                channel.send(response)
                channel.close()
                break
            elif cmd_str == 'pwd':
                response = b'\n/usr/local/\r\n'
            elif cmd_str == 'whoami':
                response = b'\nroot, but not the kind you are looking for ;)\r\n'
            elif cmd_str == 'ls' or cmd_str == 'ls -a':
                response = fake_ls(cmd_str)
                if response is None:
                    response = b'docker-compose.yml\nflag.txt\nimportant.key\nvirus.sh\r\n'
            elif cmd_str == 'cat docker-compose.yml':
                response = b'\nAt least you tried\r\n'
            elif cmd_str == 'uname -a':
                response = b'\nLinux honeypot-box 5.13.13-darkmagic #1 SMP Mon Never x86_64 GNU/Linux\r\n'
            elif cmd_str == 'id':
                response = b'uid=0(root) gid=0(root) groups=0(root)\r\n'
            elif cmd_str == 'cat /etc/passwd':
                response = b'root:x:0:0:root:/root:/bin/bash\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\r\n'
            elif cmd_str == 'rm -rf /':
                response = b'Nice try. System is still smiling at you. ^_^\r\n'
            elif 'wget' in cmd_str:
                stats["Malware Dropped"] += 1
                response = b'Connecting to totally-real-download.site...\nError: site filled with glitter. Download failed.\r\n'
            elif 'curl' in cmd_str:
                response = b'Sure, curl that into your imagination.\r\n'
            elif cmd_str == 'netstat -an':
                response = b'\nActive connections? Nah, it is a monastery in here.\r\n'
            elif cmd_str == 'ps aux':
                response = b'\nUSER PID %CPU %MEM COMMAND\nroot 1 0.0 0.0 /bin/dance_party\r\n'
            elif cmd_str == 'top':
                response = b'\nPID USER PR NI VIRT RES SHR S %CPU %MEM TIME+ COMMAND\n1 root 20 0 1234 1234 1234 R 100 100.0 0:00.01 illusion\r\n'
            elif cmd_str == 'history':
                response = b'\n1 echo "You thought I would give you that?"\n2 nice try\n3 rm -rf hope\r\n'
            elif 'chmod' in cmd_str:
                response = b'Permissions? Sure, you are *permitted* to have hope.\r\n'
            elif cmd_str == 'sudo su':
                response = b'\nWe do not sudo here. Just vibes.\r\n'
            elif cmd_str == 'su':
                response = b'\nAuthentication failed. Are you even trying?\r\n'
            elif cmd_str == 'mount /dev/sda1 /mnt':
                response = b'\nError: device mounted to disappointment\r\n'
            elif cmd_str.startswith('dd if='):
                response = b'\n/dev/null has rejected your request for a clone army.\r\n'
            elif './' in cmd_str:
                response = b'./malware: command not found\nDid you mean: ./maybe-next-time\r\n'
            elif 'crontab' in cmd_str:
                response = b'\nNo cron, only chaos.\r\n'
            elif 'adduser' in cmd_str or 'useradd' in cmd_str:
                response = b'\nUser added to shadow realm.\r\n'
            elif 'ssh-keygen' in cmd_str:
                response = b'\nGenerating keys...\nOops. Dropped them.\r\n'
            elif 'python -c' in cmd_str or 'perl -e' in cmd_str:
                response = b'\nScripting dreams into a sandboxed void...\r\n'
            else:
                response = b'\n' + cmd_str.encode() + b'\r\n'
            channel.send(response)
            channel.send(b'prod-server3$ ')
            command = b""
            time.sleep(0.1)

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password
        self.failed_attempts = 0
        self.session_username = None

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        self.session_username = username
        funnel_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}')
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                self.failed_attempts += 1
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_env_request(self, channel, name, value):
        return True

def client_handler(client, addr, username, password):
    client_ip = addr[0]
    stats["Logged IPs"] += 1
    print(f"{client_ip} has connected to the server")
    transport = None
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.add_server_key(host_key)
        transport.start_server(server=server)
        channel = transport.accept(100)
        if channel is None:
            print("No channel opened.")
            return
        standard_banner = generate_banner()
        channel.send(standard_banner.encode())
        emulated_shell(channel, client_ip=client_ip, failed_attempts=server.failed_attempts)
    except Exception as error:
        print(f"Error in client handler: {error}")
    finally:
        try:
            if transport:
                transport.close()
            client.close()
        except Exception as error:
            print(f"Error while closing: {error}")

def honeypot(address, port, username, password):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))
    socks.listen(50)
    print(f"SSH server is active and listening on port {port}")

    threading.Thread(target=show_face, args=("sleeping", stats, recent_activity), daemon=True).start()

    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handler, args=(client, addr, username, password))
            ssh_honeypot_thread.daemon = True
            ssh_honeypot_thread.start()
        except Exception as error:
            print(f"Error in honeypot listener: {error}")

if __name__ == "__main__":
    honeypot('0.0.0.0', 2223, None, None)