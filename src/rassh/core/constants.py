from enum import IntEnum
from typing import Optional


class ActionType(IntEnum):
    ALLOW = 0
    DELAY = 1
    FAKE = 2
    INSULT = 3
    BLOCK = 4


class CommandType(IntEnum):
    UNKNOWN = 0
    DOWNLOAD = 1
    EXECUTE = 2


# Global state (to be replaced with proper state management)
class GlobalState:
    
    def __init__(self):
        self.current_command: Optional[str] = None
        self.current_reward: Optional[float] = None
        self.prev_command: Optional[str] = None
        self.rl_action: Optional[int] = None
        self.rl_params: str = ""
    
    def reset(self):
        """Reset global state."""
        self.current_command = None
        self.current_reward = None
        self.prev_command = None
        self.rl_action = None
        self.rl_params = ""


# Global state instance
global_state = GlobalState()