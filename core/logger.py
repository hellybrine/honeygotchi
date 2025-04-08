# core/logger.py
import os
import datetime
import json

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "honeygotchi.log")

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_msg = f"{timestamp} {message}"
        print(full_msg)  # Console log

        with open(self.log_file, "a") as f:
            f.write(full_msg + "\n")

    def collect_stats(self):
        stats = {}

        # Cowrie stats
        cowrie_log = "/opt/cowrie/log/cowrie.json"
        if os.path.exists(cowrie_log):
            with open(cowrie_log, "r") as f:
                lines = f.readlines()
            stats["cowrie_connection_count"] = len(lines)
        else:
            stats["cowrie_connection_count"] = 0

        # Dionaea stats
        dionaea_log = "/opt/dionaea/var/log/dionaea.log"
        if os.path.exists(dionaea_log):
            with open(dionaea_log, "r") as f:
                lines = f.readlines()
            stats["dionaea_event_count"] = len(lines)
        else:
            stats["dionaea_event_count"] = 0

        # Honeyd stats
        honeyd_log = "/var/log/honeyd.log"
        if os.path.exists(honeyd_log):
            with open(honeyd_log, "r") as f:
                lines = f.readlines()
            stats["honeyd_event_count"] = 0
        else:
            stats["honeyd_event_count"] = 0

        stats["timestamp"] = datetime.datetime.now().isoformat()
        
        self._save_stats(stats)
        return stats

    def _save_stats(self, stats):
        stats_file = os.path.join(self.log_dir, "stats.json")
        try:
            if os.path.exists(stats_file):
                with open(stats_file, "r") as f:
                    all_stats = json.load(f)
            else:
                all_stats = []

            all_stats.append(stats)

            with open(stats_file, "w") as f:
                json.dump(all_stats, f, indent=2)
        except Exception as e:
            self.log(f"[Logger] Error saving stats: {e}")