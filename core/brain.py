# core/brain.py
class Brain:
    def __init__(self):
        self.last_reward = 0

    def evaluate(self, stats):
        """
        Simple heuristic-based scoring for now.
        Later: Replace this with reinforcement learning.
        """
        reward = 0

        # Basic scoring for now
        reward += stats.get("cowrie_connection_count", 0) * 1.5
        reward += stats.get("dionaea_event_count", 0) * 1.2
        reward += stats.get("honeyd_event_count", 0) * 1.0

        # Testing diminishing returns
        reward = min(reward, 100)  # Clamp max value

        # Averaging with previous
        self.last_reward = (self.last_reward * 0.6) + (reward * 0.4)
        return self.last_reward
