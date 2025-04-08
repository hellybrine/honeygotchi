# services/base_service.py
from abc import ABC, abstractmethod

class BaseService(ABC):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_stats(self):
        return {}