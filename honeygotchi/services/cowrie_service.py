# services/cowrie_service.py
import subprocess
import os
from services.base_service import BaseService

class CowrieService(BaseService):
    def __init__(self, logger, path="/opt/cowrie"):
        super().__init__(logger)
        self.path = path

    def start(self):
        self.logger.log("[Cowrie] Starting...")
        subprocess.call(["bin/cowrie", "start"], cwd=self.path)

    def stop(self):
        self.logger.log("[Cowrie] Stopping...")
        subprocess.call(["bin/cowrie", "stop"], cwd=self.path)

    def get_stats(self):
        log_path = os.path.join(self.path, "log", "cowrie.json")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                lines = f.readlines()
            return {"cowrie_connections": len(lines)}
        return {"cowrie_connections": 0}