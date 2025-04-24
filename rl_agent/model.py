import numpy as np
import os
import pickle
from sklearn.linear_model import SGDClassifier
import logging

logger = logging.getLogger('rl_agent')

class RLAgent:
    """Lightweight RL agent for honeypot command decision-making"""
    
    def __init__(self, config):
        self.config = config
        self.actions = ['allow', 'block', 'substitute', 'delay', 'insult']
        self.model = SGDClassifier(loss='log_loss', warm_start=True)
        self.epsilon = config['rl']['epsilon']  # Exploration rate
        self.state_history = []
        self.action_history = []
        self.reward_history = []
        
        # Load existing model
        self._load_model()
        
    def decide_action(self, state_features):
        """Determine action for given state using ε-greedy strategy"""
        if np.random.random() < self.epsilon:
            action_idx = np.random.randint(0, len(self.actions))
            return self.actions[action_idx]
            
        try:
            if hasattr(self.model, 'classes_'):
                action_idx = self.model.predict([state_features])[0]
                return self.actions[action_idx]
        except Exception as e:
            logger.error(f"Model prediction error: {e}")
            
        return self.actions[0]
        
    def update(self, state_features, action, reward):
        """Update model with new experience"""
        action_idx = self.actions.index(action)
        
        # Store experience
        self.state_history.append(state_features)
        self.action_history.append(action)
        self.reward_history.append(reward)
        
        if not hasattr(self.model, 'classes_'):
            self.model.partial_fit([state_features], [action_idx], 
                                  classes=range(len(self.actions)))
        else:
            self.model.partial_fit([state_features], [action_idx])
            
        if len(self.state_history) % self.config['rl']['save_interval'] == 0:
            self._save_model()
            
        return True
        
    def _extract_features(self, command):
        """Convert command to feature vector"""
        return np.array([
            int('wget' in command),
            int('curl' in command),
            int('./' in command),
            int('sudo' in command),
            int('rm' in command),
            int('chmod' in command),
            len(command)
        ], dtype=np.float32)
        
    def calculate_reward(self, command, action):
        """Calculate reward based on action and command context"""
        malicious_commands = ['rm', 'wget', 'curl', 'chmod', './']
        is_malicious = any(cmd in command for cmd in malicious_commands)
        rewards = {
            'allow': 0.5 if not is_malicious else -1.0,
            'block': 0.8 if is_malicious else -0.5,
            'substitute': 0.3,
            'delay': 0.1,
            'insult': -0.1
        }
        
        return rewards.get(action, 0.0)
        
    def _save_model(self):
        """Save model to disk"""
        os.makedirs(self.config['rl']['model_dir'], exist_ok=True)
        model_path = os.path.join(self.config['rl']['model_dir'], 'rl_model.pkl')
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            
    def _load_model(self):
        """Load model from disk if exists"""
        model_path = os.path.join(self.config['rl']['model_dir'], 'rl_model.pkl')
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Model loaded from {model_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                
        return False