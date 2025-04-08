# services/bait_manager.py
from services.cowrie_service import CowrieService

class BaitManager:
    def __init__(self, logger):
        self.logger = logger
        self.services = [
            CowrieService(logger)
        ]

    def start_services(self):
        self.logger.log("[BaitManager] Starting honeypot services...")
        for service in self.services:
            service.start()

    def stop_services(self):
        self.logger.log("[BaitManager] Stopping honeypot services...")
        for service in self.services:
            service.stop()

    def collect_stats(self):
        stats = {}
        for service in self.services:
            stats.update(service.get_stats())
        return stats