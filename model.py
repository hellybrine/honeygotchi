import torch
import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, Any

class ModelManager:
    """Utility class for managing RL models"""
    
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
    
    def save_checkpoint(self, model, optimizer, epoch, loss, filepath):
        """Save training checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
            'timestamp': datetime.now().isoformat()
        }
        torch.save(checkpoint, filepath)
        print(f"Checkpoint saved: {filepath}")
    
    def load_checkpoint(self, model, optimizer, filepath):
        """Load training checkpoint"""
        if not os.path.exists(filepath):
            print(f"Checkpoint not found: {filepath}")
            return None
        
        checkpoint = torch.load(filepath, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        return {
            'epoch': checkpoint['epoch'],
            'loss': checkpoint['loss'],
            'timestamp': checkpoint.get('timestamp', 'Unknown')
        }
    
    def export_model_info(self, model_path, output_path):
        """Export model information to JSON"""
        if not os.path.exists(model_path):
            print(f"Model not found: {model_path}")
            return
        
        model_data = torch.load(model_path, map_location='cpu')
        
        info = {
            'model_path': model_path,
            'export_timestamp': datetime.now().isoformat(),
            'model_size_mb': os.path.getsize(model_path) / (1024 * 1024),
            'epsilon': model_data.get('epsilon', 'Unknown'),
            'actions': model_data.get('actions', {}),
            'training_data_count': len(model_data.get('training_data', [])),
            'networks': list(model_data.keys())
        }
        
        with open(output_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"Model info exported: {output_path}")
    
    def validate_model(self, model_path):
        """Validate model integrity"""
        try:
            model_data = torch.load(model_path, map_location='cpu')
            required_keys = [
                'engagement_net_state_dict',
                'deception_net_state_dict', 
                'security_net_state_dict',
                'collection_net_state_dict'
            ]
            
            missing_keys = [key for key in required_keys if key not in model_data]
            
            if missing_keys:
                print(f"Model validation failed. Missing keys: {missing_keys}")
                return False
            
            print("Model validation passed!")
            return True
            
        except Exception as e:
            print(f"Model validation error: {e}")
            return False

def analyze_training_data(data_path):
    """Analyze training data statistics"""
    if not os.path.exists(data_path):
        print(f"Training data not found: {data_path}")
        return
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    if not data:
        print("No training data found")
        return
    
    # Calculate statistics
    total_sessions = len(data)
    total_commands = sum(len(session.get('session_data', {}).get('commands', [])) for session in data)
    avg_session_duration = np.mean([session.get('session_data', {}).get('session_duration', 0) for session in data])
    
    # Attacker types
    attacker_types = [session.get('session_data', {}).get('attacker_type', 'unknown') for session in data]
    attacker_distribution = {atype: attacker_types.count(atype) for atype in set(attacker_types)}
    
    # Rewards
    rewards = [session.get('reward', 0) for session in data]
    avg_reward = np.mean(rewards)
    
    stats = {
        'total_sessions': total_sessions,
        'total_commands': total_commands,
        'avg_session_duration': avg_session_duration,
        'avg_reward': avg_reward,
        'attacker_distribution': attacker_distribution,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    print("Training Data Analysis:")
    print("=" * 40)
    for key, value in stats.items():
        if key != 'analysis_timestamp':
            print(f"{key}: {value}")
    
    return stats