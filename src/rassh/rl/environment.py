import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Tuple, Dict, Any, Optional

from ..core.constants import ActionType, CommandType, global_state


class HoneypotEnvironment(gym.Env):
    
    metadata = {"render_modes": ["human"]}
    
    def __init__(self, render_mode: Optional[str] = None):
        super().__init__()
        
        # Action space: 5 possible actions
        self.action_space = spaces.Discrete(len(ActionType))
        
        # Observation space: command features
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(10,), dtype=np.float32
        )
        
        self.render_mode = render_mode
        self.current_step = 0
        self.max_steps = 1000
        
    def reset(
        self, 
        seed: Optional[int] = None, 
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset environment."""
        super().reset(seed=seed)
        
        self.current_step = 0
        global_state.reset()
        
        observation = self._get_observation()
        info = {}
        
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """execute action and return results"""
        self.current_step += 1
        
        # Store action
        global_state.rl_action = action
        
        # Get reward
        reward = self._calculate_reward(action)
        
        # Check if episode is done
        terminated = self.current_step >= self.max_steps
        truncated = False
        
        observation = self._get_observation()
        info = {"action": action, "step": self.current_step}
        
        return observation, reward, terminated, truncated, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation."""
        # Create feature vector from current command
        if global_state.current_command:
            features = self._extract_command_features(global_state.current_command)
        else:
            features = np.zeros(10, dtype=np.float32)
        
        return features
    
    def _extract_command_features(self, command: str) -> np.ndarray:
        """Extract features from command."""
        features = np.zeros(10, dtype=np.float32)
        
        # Basic command features
        features[0] = len(command) / 100.0  # Normalized length
        features[1] = float('wget' in command)
        features[2] = float('curl' in command)
        features[3] = float('python' in command)
        features[4] = float('bash' in command)
        features[5] = float('sh' in command)
        features[6] = float(command.startswith('./'))
        features[7] = float('http' in command)
        features[8] = float('ftp' in command)
        features[9] = float(any(char in command for char in ';&|'))
        
        return features
    
    def _calculate_reward(self, action: int) -> float:
        """Calculate reward for action."""
        if not global_state.current_command:
            return 0.0
        
        command = global_state.current_command
        
        # Reward based on command type and action
        if self._is_malicious_command(command):
            if action == ActionType.BLOCK:
                return 1.0
            elif action == ActionType.INSULT:
                return 0.8
            elif action == ActionType.FAKE:
                return 0.6
            else:
                return -0.5
        else:
            if action == ActionType.ALLOW:
                return 0.5
            else:
                return -0.2
    
    def _is_malicious_command(self, command: str) -> bool:
        """Determine if command is potentially malicious."""
        malicious_patterns = [
            'wget', 'curl', 'nc', 'netcat', 'python -c',
            'bash -c', 'sh -c', '/tmp/', 'chmod +x'
        ]
        return any(pattern in command.lower() for pattern in malicious_patterns)
    
    def render(self):
        """Render environment state."""
        if self.render_mode == "human":
            print(f"Step: {self.current_step}")
            print(f"Current command: {global_state.current_command}")
            print(f"Last action: {global_state.rl_action}")