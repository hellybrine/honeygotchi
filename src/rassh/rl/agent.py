import torch
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from typing import Optional
import structlog

from .environment import HoneypotEnvironment
from ..core.config import RLConfig

logger = structlog.get_logger()


class HoneypotCallback(BaseCallback):
    """callback for training monitoring."""
    
    def __init__(self, verbose: int = 0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        """Called at each step."""
        return True
    
    def _on_rollout_end(self) -> None:
        """Called at end of rollout."""
        if len(self.locals.get('episode_rewards', [])) > 0:
            mean_reward = np.mean(self.locals['episode_rewards'])
            logger.info("Training progress", mean_reward=mean_reward)


class HoneypotAgent:
    """agent for honeypot decision making."""
    
    def __init__(self, config: RLConfig):
        self.config = config
        self.env = None
        self.model = None
        self._setup_environment()
        self._setup_model()
    
    def _setup_environment(self):
        """Setup the RL environment."""
        env = HoneypotEnvironment()
        self.env = DummyVecEnv([lambda: env])
    
    def _setup_model(self):
        """DQN setup"""
        policy_kwargs = dict(
            net_arch=[64, 64],
            activation_fn=torch.nn.ReLU
        )
        
        self.model = DQN(
            "MlpPolicy",
            self.env,
            learning_rate=self.config.learning_rate,
            buffer_size=self.config.memory_size,
            batch_size=self.config.batch_size,
            gamma=self.config.gamma,
            exploration_fraction=0.1,
            exploration_initial_eps=1.0,
            exploration_final_eps=self.config.epsilon,
            policy_kwargs=policy_kwargs,
            verbose=1
        )
    
    def train(self, total_timesteps: int = 10000):
        """Train"""
        callback = HoneypotCallback()
        
        logger.info("Starting RL training", timesteps=total_timesteps)
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback
        )
        logger.info("Training completed")
    
    def predict(self, observation: np.ndarray) -> int:
        """Predict action for given observation."""
        if self.model is None:
            return 0  # Default is ALLOW
        
        action, _ = self.model.predict(observation, deterministic=True)
        return int(action)
    
    def save(self, path: str):
        """Save trained model."""
        if self.model:
            self.model.save(path)
            logger.info("Model saved", path=path)
    
    def load(self, path: str):
        """Load trained model."""
        try:
            self.model = DQN.load(path, env=self.env)
            logger.info("Model loaded", path=path)
        except Exception as e:
            logger.error("Failed to load model", path=path, error=str(e))