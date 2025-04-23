import numpy as np

def featurize(session_dict):
    return np.array([
        session_dict["duration_secs"] / 60.0,
        session_dict["num_commands"] / 10.0,
        float(session_dict["bot_detected"]),
        session_dict["fake_file_access"] / 5.0,
        1.0 if session_dict["interaction_type"] == "ssh" else 0.5 if session_dict["interaction_type"] == "api" else 0.0
    ])