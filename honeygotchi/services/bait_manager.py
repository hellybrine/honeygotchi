# services/bait_manager.py
from services.cowrie_service import CowrieService
from services.honeyd_service import HoneydService
from services.dionaea_service import DionaeaService

class BaitManager:
    def __init__(self, logger):
        self.logger = logger
        self.services = [
            CowrieService(logger),
            HoneydService(logger),
            DionaeaService(logger)
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