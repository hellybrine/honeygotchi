class RewardFunction:
    def __call__(self, session_dict):
        reward = 0
        reward += session_dict["duration_secs"] * 0.1
        reward += session_dict["num_commands"] * 0.2
        reward += session_dict["fake_file_access"] * 0.3
        if session_dict["bot_detected"]:
            reward -= 1.0
        return reward
