# services/dionaea_service.py
import subprocess
import os
from services.base_service import BaseService

class DionaeaService(BaseService):
    def __init__(self, logger, path="/opt/dionaea"):
        super().__init__(logger)
        self.path = path
        self.process = None

    def start(self):
        self.logger.log("[Dionaea] Starting...")
        cmd = ["bin/dionaea"]
        self.process = subprocess.Popen(cmd, cwd=self.path)

    def stop(self):
        self.logger.log("[Dionaea] Stopping...")
        if self.process:
            self.process.terminate()

    def get_stats(self):
        log_path = os.path.join(self.path, "log", "dionaea.log")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                lines = f.readlines()
            return {"dionaea_events": len(lines)}
        return {"dionaea_events": 0}
