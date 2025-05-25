# test_model.py
import torch
import json

try:
    model_data = torch.load('models/enhanced_rl_model.pth', map_location='cpu')
    print("Main RL model loaded successfully")
    print(f"  - Epsilon: {model_data['epsilon']}")
    print(f"  - Actions: {list(model_data['actions'].keys())}")
except Exception as e:
    print(f"✗ Error loading main model: {e}")

# Test loading production models
production_models = [
    'models/engagement_net.pt',
    'models/deception_net.pt', 
    'models/security_net.pt',
    'models/collection_net.pt'
]

for model_path in production_models:
    try:
        model = torch.jit.load(model_path, map_location='cpu')
        print(f"{model_path} loaded successfully")
    except Exception as e:
        print(f"✗ Error loading {model_path}: {e}")

# Test metadata
try:
    with open('models/model_metadata.json', 'r') as f:
        metadata = json.load(f)
    print("✓ Model metadata loaded successfully")
    print(f"  - Export date: {metadata.get('export_date', 'Unknown')}")
    print(f"  - Training interactions: {metadata.get('training_interactions', 'Unknown')}")
except Exception as e:
    print(f"✗ Error loading metadata: {e}")