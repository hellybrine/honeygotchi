import numpy as np
import structlog
from typing import List, Dict, Any, Tuple
from collections import deque
import pickle
from pathlib import Path

logger = structlog.get_logger()


class ReplayBuffer:
    """Experience replay buffer for RL training."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Add experience to buffer."""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> List[Tuple]:
        """Sample batch from buffer."""
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]
    
    def __len__(self):
        return len(self.buffer)


class CommandFeatureExtractor:
    """Extract features from commands for RL."""
    
    def __init__(self):
        self.malicious_patterns = [
            'wget', 'curl', 'nc', 'netcat', 'python -c', 'bash -c', 'sh -c',
            '/tmp/', 'chmod +x', 'base64', 'echo', 'cat >', 'dd if=', 'rm -rf',
            'killall', 'pkill', 'nohup', '&', '|', ';', '&&', '||'
        ]
        
        self.download_patterns = [
            'wget', 'curl', 'ftp', 'scp', 'rsync'
        ]
        
        self.execution_patterns = [
            'python', 'perl', 'ruby', 'php', 'bash', 'sh', 'zsh', './', 'exec'
        ]
    
    def extract_features(self, command: str) -> np.ndarray:
        """Extract feature vector from command."""
        features = np.zeros(20, dtype=np.float32)
        
        command_lower = command.lower()
        
        # Basic features
        features[0] = len(command) / 100.0  # length
        features[1] = len(command.split()) / 20.0  # word count
        features[2] = float(any(char.isdigit() for char in command))  # contains digits
        features[3] = float(any(char in '!@#$%^&*()' for char in command))  # special chars
        
        # malicious pattern
        for i, pattern in enumerate(self.malicious_patterns[:10]):
            features[4 + i] = float(pattern in command_lower)
        
        # download patterns
        features[14] = float(any(pattern in command_lower for pattern in self.download_patterns))
        
        # execution patterns
        features[15] = float(any(pattern in command_lower for pattern in self.execution_patterns))
        
        # network-related
        features[16] = float('http' in command_lower or 'ftp' in command_lower)
        features[17] = float(any(port in command for port in ['80', '443', '21', '22', '23']))
        
        # file operations
        features[18] = float(any(op in command_lower for op in ['>', '>>', '<', '<<']))
        
        # suspicious combinations
        features[19] = float('wget' in command_lower and 'chmod' in command_lower)
        
        return features


class RLMetrics:
    
    def __init__(self):
        self.episode_rewards = []
        self.episode_lengths = []
        self.action_counts = {i: 0 for i in range(5)}
        self.command_types = {'malicious': 0, 'benign': 0}
    
    def record_episode(self, reward: float, length: int):
        """record metrics"""
        self.episode_rewards.append(reward)
        self.episode_lengths.append(length)
    
    def record_action(self, action: int):
        """record action"""
        self.action_counts[action] += 1
    
    def record_command_type(self, is_malicious: bool):
        if is_malicious:
            self.command_types['malicious'] += 1
        else:
            self.command_types['benign'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.episode_rewards:
            return {}
        
        return {
            'mean_reward': np.mean(self.episode_rewards[-100:]),  # Last 100 eps
            'mean_length': np.mean(self.episode_lengths[-100:]),
            'total_episodes': len(self.episode_rewards),
            'action_distribution': self.action_counts.copy(),
            'command_distribution': self.command_types.copy()
        }
    
    def save(self, path: Path):
        try:
            with open(path, 'wb') as f:
                pickle.dump({
                    'episode_rewards': self.episode_rewards,
                    'episode_lengths': self.episode_lengths,
                    'action_counts': self.action_counts,
                    'command_types': self.command_types
                }, f)
            logger.info("Metrics saved", path=str(path))
        except Exception as e:
            logger.error("Failed to save metrics", error=str(e))
    
    def load(self, path: Path):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.episode_rewards = data['episode_rewards']
                self.episode_lengths = data['episode_lengths']
                self.action_counts = data['action_counts']
                self.command_types = data['command_types']
            logger.info("Metrics loaded", path=str(path))
        except Exception as e:
            logger.error("Failed to load metrics", error=str(e))


def calculate_reward(command: str, action: int, client_info: Dict[str, Any]) -> float:
    extractor = CommandFeatureExtractor()
    features = extractor.extract_features(command)
    
    is_malicious = (
        features[14] > 0 or     # Download patterns
        features[15] > 0 or     # Execution patterns
        features[16] > 0 or     # Network patterns
        features[19] > 0        # Suspicious combinations
    )
    
    if is_malicious:
        if action == 4:         # BLOCK
            reward = 1.0
        elif action == 3:       # INSULT
            reward = 0.8
        elif action == 2:       # FAKE
            reward = 0.6
        elif action == 1:       # DELAY
            reward = 0.4
        else:  # ALLOW
            reward = -0.5
    else:
        if action == 0:         # ALLOW
            reward = 0.5
        elif action == 1:       # DELAY
            reward = 0.2
        else:
            reward = -0.2
    
    if client_info.get('repeat_offender', False):
        if action in [3, 4]:    # INSULT or BLOCK
            reward += 0.2
    
    return reward