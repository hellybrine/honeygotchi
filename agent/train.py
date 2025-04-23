from stable_baselines3 import A2C
from agent.honeypot_env import HoneypotEnv

env = HoneypotEnv()

model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

model.save("training/model/honeypot_a2c")