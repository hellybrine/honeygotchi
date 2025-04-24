import random
import time

def generate_banner():
    load = f"{random.uniform(0.0, 1.0):.2f}, {random.uniform(0.0, 1.0):.2f}, {random.uniform(0.0, 1.0):.2f}"
    uptime = random.randint(1, 100)  # Random uptime in days
    last_login = time.strftime("%a %b %d %H:%M:%S %Y")  # Current time as last login
    
    banner = f"""
    Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)
    * Documentation:  https://help.ubuntu.com
    * Management:     https://example.com/manage
    * Security updates:  https://ubuntu.com/security
    * System load:     {load}
    * Uptime:          {uptime} days, {random.randint(0, 23)} hours, {random.randint(0, 59)} minutes

    Last login: {last_login} from {random.choice(['192.168.1.10', '192.168.1.12', '192.168.1.15'])}

    # For system administration, use sudo.
    # To learn more about using this system, visit https://help.ubuntu.com/
    """
    
    return banner

standard_banner = generate_banner()
