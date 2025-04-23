import gym
from gym.spaces import MultiDiscrete, Box
import numpy as np

from agent.session import Session
from agent.featurizer import featurize
from agent.reward import RewardFunction
from agent.parameter import Parameter


class HoneypotEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.params = [
            Parameter("response_delay", 0, 5),
            Parameter("fake_file_access", 0, 3)
        ]

        self.action_space = MultiDiscrete([p.space().n for p in self.params])
        self.observation_space = Box(low=0, high=1, shape=(5,), dtype=np.float32)

        self.session = Session()
        self.reward_fn = RewardFunction()

    def step(self, action):
        self.session = Session()
        self.session.simulate_interaction()

        for i, p in enumerate(self.params):
            p.apply(action[i], self.session)

        session_dict = self.session.to_dict()
        reward = self.reward_fn(session_dict)
        obs = featurize(session_dict)
        done = False

        return obs, reward, done, {}

    def reset(self):
        self.session = Session()
        self.session.simulate_interaction()
        return featurize(self.session.to_dict())
