import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import os
import json
from collections import deque
from typing import Dict, List, Tuple

class EnhancedRLAgent:
    """Enhanced RL agent with PyTorch backend"""
    
    def __init__(self, state_dim=15, action_dim=5, hidden_dim=128, lr=0.001):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.actions = {
            'engagement': ['minimal_response', 'standard_response', 'detailed_response', 'enhanced_response', 'eject_user'],
            'deception': ['reveal_fake_files', 'hide_sensitive_data', 'modify_file_contents', 'simulate_network_topology', 'create_false_users'],
            'security': ['isolate_session', 'monitor_closely', 'redirect_to_sandbox', 'limit_privileges', 'log_extensively'],
            'collection': ['prompt_for_credentials', 'request_tool_upload', 'simulate_error_logs', 'capture_keystrokes', 'analyze_techniques']
        }
        
        self.max_actions = max(len(actions) for actions in self.actions.values())
        
        self.engagement_net = self._build_network(state_dim, self.max_actions, hidden_dim)
        self.deception_net = self._build_network(state_dim, self.max_actions, hidden_dim)
        self.security_net = self._build_network(state_dim, self.max_actions, hidden_dim)
        self.collection_net = self._build_network(state_dim, self.max_actions, hidden_dim)
        
        self.optimizers = {
            'engagement': optim.Adam(self.engagement_net.parameters(), lr=lr),
            'deception': optim.Adam(self.deception_net.parameters(), lr=lr),
            'security': optim.Adam(self.security_net.parameters(), lr=lr),
            'collection': optim.Adam(self.collection_net.parameters(), lr=lr)
        }
        
        self.memory = deque(maxlen=10000)
        self.batch_size = 64
        
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        self.training_data = []

    def _build_network(self, state_dim, action_dim, hidden_dim):
        """Build neural network for each objective"""
        return nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Linear(hidden_dim//2, action_dim),
            nn.Softmax(dim=-1)
        ).to(self.device)

    def get_state(self, session_data):
        """Convert session data to state vector (compatible with existing format)"""
        return np.array([
            session_data.get('commands_count', 0) / 100.0,
            session_data.get('session_duration', 0) / 3600.0,
            session_data.get('unique_commands', 0) / 50.0,
            session_data.get('file_access_attempts', 0) / 20.0,
            session_data.get('malware_downloads', 0) / 10.0,
            session_data.get('privilege_escalation_attempts', 0) / 10.0,
            session_data.get('network_scan_attempts', 0) / 10.0,
            session_data.get('persistence_attempts', 0) / 10.0,
            session_data.get('data_exfiltration_attempts', 0) / 10.0,
            session_data.get('failed_commands', 0) / 20.0,
            session_data.get('suspicious_patterns', 0) / 10.0,
            session_data.get('avg_time_between_commands', 0) / 30.0,
            session_data.get('command_complexity_score', 0) / 10.0,
            session_data.get('repeat_command_ratio', 0),
            session_data.get('current_engagement_level', 0) / 3.0
        ], dtype=np.float32)

    def select_action(self, session_data):
        """Select actions using RL policy"""
        state = self.get_state(session_data)
        
        if random.random() < self.epsilon:
            return {
                'engagement': random.randint(0, len(self.actions['engagement']) - 1),
                'deception': random.randint(0, len(self.actions['deception']) - 1),
                'security': random.randint(0, len(self.actions['security']) - 1),
                'collection': random.randint(0, len(self.actions['collection']) - 1)
            }
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            engagement_probs = self.engagement_net(state_tensor)
            deception_probs = self.deception_net(state_tensor)
            security_probs = self.security_net(state_tensor)
            collection_probs = self.collection_net(state_tensor)
        
        return {
            'engagement': min(torch.argmax(engagement_probs).item(), len(self.actions['engagement']) - 1),
            'deception': min(torch.argmax(deception_probs).item(), len(self.actions['deception']) - 1),
            'security': min(torch.argmax(security_probs).item(), len(self.actions['security']) - 1),
            'collection': min(torch.argmax(collection_probs).item(), len(self.actions['collection']) - 1)
        }

    def remember(self, state, actions, rewards, next_state, done):
        """Store experience for training"""
        self.memory.append((state, actions, rewards, next_state, done))

    def replay(self, batch_size=32):
        """Train networks using experience replay"""
        if len(self.memory) < batch_size:
            return

        batch = random.sample(self.memory, batch_size)
        
        for objective in ['engagement', 'deception', 'security', 'collection']:
            states = torch.stack([torch.FloatTensor(exp[0]) for exp in batch]).to(self.device)
            next_states = torch.stack([torch.FloatTensor(exp[3]) for exp in batch]).to(self.device)
            
            current_q = getattr(self, f'{objective}_net')(states)
            
            with torch.no_grad():
                next_q = getattr(self, f'{objective}_net')(next_states)
                max_next_q = torch.max(next_q, dim=1)[0]
            
            targets = []
            for i, exp in enumerate(batch):
                reward = exp[2].get(objective, 0) if isinstance(exp[2], dict) else 0
                if exp[4]:  # done
                    target = reward
                else:
                    target = reward + 0.95 * max_next_q[i]
                targets.append(target)
            
            targets = torch.FloatTensor(targets).to(self.device)
            
            actions = torch.LongTensor([exp[1].get(objective, 0) for exp in batch]).to(self.device)
            current_q_values = current_q.gather(1, actions.unsqueeze(1)).squeeze()
            
            loss = nn.MSELoss()(current_q_values, targets)
            
            self.optimizers[objective].zero_grad()
            loss.backward()
            self.optimizers[objective].step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self, filepath='models/enhanced_rl_model.pth'):
        """Save the trained model"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        torch.save({
            'engagement_net_state_dict': self.engagement_net.state_dict(),
            'deception_net_state_dict': self.deception_net.state_dict(),
            'security_net_state_dict': self.security_net.state_dict(),
            'collection_net_state_dict': self.collection_net.state_dict(),
            'engagement_optimizer_state_dict': self.optimizers['engagement'].state_dict(),
            'deception_optimizer_state_dict': self.optimizers['deception'].state_dict(),
            'security_optimizer_state_dict': self.optimizers['security'].state_dict(),
            'collection_optimizer_state_dict': self.optimizers['collection'].state_dict(),
            'epsilon': self.epsilon,
            'actions': self.actions,
            'training_data': self.training_data
        }, filepath)

    def load_model(self, filepath='models/enhanced_rl_model.pth'):
        """Load a trained model"""
        if not os.path.exists(filepath):
            print(f"Model file {filepath} not found. Using fresh model.")
            return
        
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.engagement_net.load_state_dict(checkpoint['engagement_net_state_dict'])
        self.deception_net.load_state_dict(checkpoint['deception_net_state_dict'])
        self.security_net.load_state_dict(checkpoint['security_net_state_dict'])
        self.collection_net.load_state_dict(checkpoint['collection_net_state_dict'])
        
        self.optimizers['engagement'].load_state_dict(checkpoint['engagement_optimizer_state_dict'])
        self.optimizers['deception'].load_state_dict(checkpoint['deception_optimizer_state_dict'])
        self.optimizers['security'].load_state_dict(checkpoint['security_optimizer_state_dict'])
        self.optimizers['collection'].load_state_dict(checkpoint['collection_optimizer_state_dict'])
        
        self.epsilon = checkpoint['epsilon']
        self.actions = checkpoint['actions']
        self.training_data = checkpoint.get('training_data', [])
        
        print(f"Model loaded from {filepath}")

    def export_for_production(self, filepath='models/production_model.pt'):
        """Export model for production deployment"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        example_input = torch.randn(1, 15).to(self.device)
        
        engagement_scripted = torch.jit.trace(self.engagement_net, example_input)
        deception_scripted = torch.jit.trace(self.deception_net, example_input)
        security_scripted = torch.jit.trace(self.security_net, example_input)
        collection_scripted = torch.jit.trace(self.collection_net, example_input)
        
        # Save scripted models
        engagement_scripted.save('models/engagement_net.pt')
        deception_scripted.save('models/deception_net.pt')
        security_scripted.save('models/security_net.pt')
        collection_scripted.save('models/collection_net.pt')
        
        metadata = {
            'actions': self.actions,
            'epsilon': self.epsilon
        }
        
        with open('models/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Production models exported to models/ directory")