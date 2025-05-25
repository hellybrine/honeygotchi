"""Honeygotchi - Adaptive SSH Honeypot."""

__version__ = "1.0.0"
__author__ = "Hellybrine"
__description__ = "A modern take on a SSH honeypot; combined with reinforcement learning"

from .core.config import get_config
from .core.honeypot import HoneypotServer

__all__ = ["get_config", "HoneypotServer"]