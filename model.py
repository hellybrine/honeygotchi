import joblib
import os

MODEL_PATH = os.path.join('models', 'randomforest_classifier.pkl')
ENCODER_PATH = os.path.join('models', 'user_encoder.pkl')

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Trained model not found at models/randomforest_classifier.pkl")
    return joblib.load(MODEL_PATH)

def load_encoder():
    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError("User encoder not found at models/user_encoder.pkl")
    return joblib.load(ENCODER_PATH)

def predict_attack(features_df):
    """
    Predict attack type given a DataFrame of features.
    """
    model = load_model()
    prediction = model.predict(features_df)
    return "Malicious" if prediction[0] == 1 else "Normal"