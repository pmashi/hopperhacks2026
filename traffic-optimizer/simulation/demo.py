import gymnasium as gym
import sumo_rl
from stable_baselines3 import DQN
import pandas as pd
import os


print("Loading trained AI Traffic Optimizer...")

# Initialize environment with the GUI turned ON
env = gym.make(
    'sumo-rl-v0',
    net_file='data/intersect.net.xml',
    route_file='data/routes.rou.xml',
    use_gui=True, 
    num_seconds=100000 # A shorter 5-minute run for the live demo
)

# Load the model you saved earlier in train.py
model = DQN.load("outputs/dqn_traffic_optimizer")

obs, info = env.reset()
done = False

metrics_log = []
while not done:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    if info:
        metrics_log.append(info) # Capture the data

env.close()