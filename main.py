# import numpy as np
# import random

# class MockTrafficEnv:
#     """A simple intersection simulation."""
#     def __init__(self):
#         # State: [Cars North-South, Cars East-West]
#         self.state = [random.randint(0, 10), random.randint(0, 10)]
#         self.actions = [0, 1]  # 0: Green NS, 1: Green EW

#     def step(self, action):
#         # Calculate 'pollution' (reward) based on total idling cars
#         reward = -(self.state[0] + self.state[1])
#         # Simulate traffic moving
#         if action == 0: # Green North-South
#             self.state[0] = max(0, self.state[0] - 3)
#             self.state[1] += random.randint(0, 2) # New cars arrive EW
#         else: # Green East-West
#             self.state[1] = max(0, self.state[1] - 3)
#             self.state[0] += random.randint(0, 2) # New cars arrive NS
            
#         return np.array(self.state), reward

# # --- Q-Learning Agent ---
# class QLearningAgent:
#     def __init__(self, states_size, actions_size):
#         self.q_table = np.zeros((states_size, states_size, actions_size))
#         self.lr = 0.1       # Learning Rate
#         self.gamma = 0.9    # Discount Factor
#         self.epsilon = 0.1  # Exploration Rate

#     def choose_action(self, state):
#         if random.uniform(0, 1) < self.epsilon:
#             return random.choice([0, 1])
#         return np.argmax(self.q_table[state[0], state[1]])

#     def learn(self, state, action, reward, next_state):
#         old_value = self.q_table[state[0], state[1], action]
#         next_max = np.max(self.q_table[next_state[0], next_state[1]])
        
#         # Q-Update Formula
#         new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
#         self.q_table[state[0], state[1], action] = new_value

# # --- Training Loop ---
# env = MockTrafficEnv()
# # Assuming max 20 cars per lane for table size
# agent = QLearningAgent(21, 2) 

# print("Training the Sorting Hat of Traffic...")
# for episode in range(1000):
#     state = env.state
#     action = agent.choose_action(state)
#     next_state, reward = env.step(action)
#     agent.learn(state, action, reward, next_state)

# print("Training Complete. Agent optimized for minimum idling emissions.")
# print(f"Final State Queue: {env.state}")

import os
import sys
import traci
import platform

# 1. Check if SUMO_HOME is set
if platform.system() == "Windows":
    sumo_home = os.environ['SUMO_HOME'] = r'C:\Program Files (x86)\Eclipse\Sumo'
elif platform.system() == "Linux":
    sumo_home = os.environ['SUMO_HOME'] = "/usr/share/sumo"

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")


sumo_binary = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
config_path = "map.sumocfg"

# --start: starts the simulation immediately without clicking 'Play'
# --quit-on-end: closes the window once the simulation is done
sumo_cmd = [sumo_binary, "-c", config_path, "--start", "--quit-on-end"]

# 3. Start the Simulation
print("Launching the Traffic Sorting Hat...")
traci.start(sumo_cmd)

step = 0
while step < 1000:
    traci.simulationStep()  # This moves the simulation 1 step forward
    
    # Logic for your Optimizer goes here!
    # Example: Check for idling cars
    # ids = traci.vehicle.getIDList()
    
    step += 1

traci.close()
print("Simulation complete.")