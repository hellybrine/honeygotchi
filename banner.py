import random
import time

def generate_banner(username="ubuntu", hostname="prod-server3"):
    last_login = time.strftime("%a %b %d %H:%M:%S %Y")
    previous_ip = random.choice([
        '192.168.1.10', '192.168.1.12', '192.168.1.15', '10.24.10.1'
    ])
    # Properly aligned columns
    banner = (
        f"Last login: {last_login} from {previous_ip}\n"
        f"{username}@{hostname}:~$ "
    )
    return banner