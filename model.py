import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def generate_synthetic_data():
    # Features: [Number of commands issued, Length of commands, Number of failed attempts]
    features = []
    labels = []
    for _ in range(1000):
        commands_issued = random.randint(1, 20)
        length_of_commands = random.randint(10, 200)
        failed_attempts = random.randint(0, 5)
        label = random.choice([0, 1]) # 0: Normal, 1: Malicious
        features.append([commands_issued, length_of_commands, failed_attempts])
        labels.append(label)
    return np.array(features), np.array(labels)

def train_model():
    features, labels = generate_synthetic_data()
    model = RandomForestClassifier(n_estimators=100)
    model.fit(features, labels)
    # Save model to models/ directory
    os.makedirs('models', exist_ok=True)
    with open(os.path.join('models', 'randomforest_classifier.pkl'), 'wb') as model_file:
        pickle.dump(model, model_file)

def predict_attack(command_data):
    model_path = os.path.join('models', 'randomforest_classifier.pkl')
    if os.path.exists(model_path):
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
        prediction = model.predict([command_data])
        return "Malicious" if prediction == 1 else "Normal"
    else:
        print("Model not found. Please train the model first.")
        return "Model not found"
