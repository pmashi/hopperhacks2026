import gymnasium as gym
import sumo_rl
from stable_baselines3 import DQN

print("Loading trained AI Traffic Optimizer...")

# Initialize environment with the GUI turned ON
env = gym.make(
    'sumo-rl-v0',
    net_file='../data/intersect.net.xml',
    route_file='../data/routes.rou.xml',
    use_gui=True, 
    num_seconds=9999999999999999999999999 # A shorter 5-minute run for the live demo
)

# Load the model you saved earlier in train.py
model = DQN.load("../outputs/dqn_traffic_optimizer")

obs, info = env.reset()
done = False

while not done:
    # deterministic=True means the AI uses its strict learned rules, no random exploring
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

env.close()