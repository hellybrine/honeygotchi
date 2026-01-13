"""State persistence manager for RL agent."""
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class StateManager:
    """Manages persistence of RL agent state."""
    
    def __init__(self, state_file: str = "rl_state.json"):
        """Initialize state manager."""
        self.state_file = state_file
        self.state_dir = os.path.dirname(state_file) or "."
        os.makedirs(self.state_dir, exist_ok=True)
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save RL agent state to file."""
        try:
            # Create backup if file exists
            if os.path.exists(self.state_file):
                backup_file = f"{self.state_file}.bak"
                with open(self.state_file, 'r') as f:
                    backup_data = f.read()
                with open(backup_file, 'w') as f:
                    f.write(backup_data)
            
            # Save new state
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug(f"State saved to {self.state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load RL agent state from file."""
        if not os.path.exists(self.state_file):
            logger.info(f"State file not found: {self.state_file}. Starting fresh.")
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            logger.info(f"State loaded from {self.state_file}")
            return state
        except json.JSONDecodeError:
            # Try backup file
            backup_file = f"{self.state_file}.bak"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r') as f:
                        state = json.load(f)
                    logger.warning(f"Loaded state from backup file: {backup_file}")
                    return state
                except Exception as e:
                    logger.error(f"Failed to load backup state: {e}")
            else:
                logger.error(f"State file corrupted and no backup available: {self.state_file}")
            return None
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None
    
    def state_exists(self) -> bool:
        """Check if state file exists."""
        return os.path.exists(self.state_file)
    
    def clear_state(self) -> bool:
        """Clear saved state."""
        try:
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            if os.path.exists(f"{self.state_file}.bak"):
                os.remove(f"{self.state_file}.bak")
            logger.info("State cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear state: {e}")
            return False
