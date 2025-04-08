# core/honeygotchi.py
import time
from core.logger import Logger
from core.brain import Brain
from services.bait_manager import BaitManager
from ui.face import Face

class Honeygotchi:
    def __init__(self):
        self.logger = Logger()
        self.brain = Brain()
        self.bait_manager = BaitManager(self.logger)
        self.face = Face()

    def run(self):
        self.logger.log("Honeygotchi started.")
        self.bait_manager.start_services()

        try:
            while True:
                stats = self.logger.collect_stats()
                reward = self.brain.evaluate(stats)
                self.face.update(reward)
                time.sleep(30)
        except KeyboardInterrupt:
            self.logger.log("Shutting down Honeygotchi...")
            self.bait_manager.stop_services()
            self.face.shutdown()