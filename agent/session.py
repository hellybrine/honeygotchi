import time
import random


class Session:
    def __init__(self):
        self.start_time = time.time()
        self.commands_run = []
        self.ip_address = "0.0.0.0"
        self.duration_secs = 0
        self.bot_detected = False
        self.interaction_type = "unknown"  # ssh, http, scan
        self.fake_file_access = 0

    def simulate_interaction(self):
        # Simulate attacker
        self.duration_secs = random.randint(2, 60)
        self.commands_run = random.choices(["ls", "cat /etc/passwd", "uname -a", "curl http://"], k=random.randint(1, 5))
        self.ip_address = random.choice(["1.2.3.4", "10.0.0.8", "198.51.100.1"])
        self.bot_detected = random.random() < 0.3
        self.interaction_type = random.choice(["ssh", "scan", "api"])
        self.fake_file_access = random.randint(0, 3)

    def to_dict(self):
        return {
            "duration_secs": self.duration_secs,
            "num_commands": len(self.commands_run),
            "bot_detected": self.bot_detected,
            "interaction_type": self.interaction_type,
            "fake_file_access": self.fake_file_access
        }