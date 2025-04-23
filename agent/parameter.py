from gym.spaces import Discrete

class Parameter:
    def __init__(self, name, min_value=0, max_value=3):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value

    def space(self):
        return Discrete(self.max_value - self.min_value + 1)

    def apply(self, value, session):
        # Apply parameter to session simulation (mock for now)
        if self.name == "response_delay":
            session.duration_secs += value  # delay increases duration
        elif self.name == "fake_file_access":
            session.fake_file_access = value
