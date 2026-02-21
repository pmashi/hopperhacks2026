import gymnasium as gym
import sumo_rl
from stable_baselines3 import DQN
import os

# 1. Define the paths to your SUMO network and route files
net_file = "intersect.net.xml"
route_file = "routes.rou.xml"

# Ensure output directory exists for our stats
os.makedirs("outputs", exist_ok=True)

# 2. Initialize the SUMO-RL Environment
# We use the Gymnasium API for a standard single-intersection setup
env = gym.make(
    'sumo-rl-v0',
    net_file=net_file,
    route_file=route_file,
    out_csv_name='outputs/traffic_stats',
    use_gui=True, # Tip: Set to False during heavy training for a massive speed boost
    num_seconds=10000 # Total simulation time per episode in seconds
)

# 3. Initialize the Deep Q-Network (DQN) Agent
# MlpPolicy creates a standard Multi-Layer Perceptron neural network.
model = DQN(
    "MlpPolicy",
    env,
    learning_rate=1e-3,
    buffer_size=50000,          # How many past experiences the AI remembers
    exploration_fraction=0.1,   # Percentage of time the AI explores random actions early on
    verbose=1                   # Prints training progress to your terminal
)



# 4. Train the AI Model
print("Starting training phase...")
# 20,000 timesteps is a good quick baseline for a hackathon test run
model.learn(total_timesteps=20000) 
print("Training complete!")

# 5. Save the trained model so you don't have to retrain for your demo
model.save("dqn_traffic_optimizer")

# 6. Test the trained agent in the visual environment
print("Testing the trained model...")
obs, info = env.reset()
done = False

while not done:
    # The agent predicts the optimal next traffic light phase based on current traffic
    action, _states = model.predict(obs, deterministic=True)
    
    # The environment executes the phase change and returns the new state and reward
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

env.close()