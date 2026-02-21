import gymnasium as gym
import sumo_rl
import pandas as pd
import os

print("Starting bulletproof baseline simulation...")

# Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

env = gym.make(
    'sumo-rl-v0',
    net_file='intersect.net.xml',
    route_file='routes.rou.xml',
    use_gui=True, 
    num_seconds=100000,
    fixed_ts=True  # Force standard traffic light logic
)

obs, info = env.reset()
done = False

# We will manually collect the data here!
metrics_log = []

while not done:
    obs, reward, terminated, truncated, info = env.step(0) 
    done = terminated or truncated
    
    # sumo-rl passes the intersection stats inside the 'info' dictionary at every step
    if info:
        metrics_log.append(info)

env.close()

# Force pandas to save it exactly how our calculator expects it
if metrics_log:
    df = pd.DataFrame(metrics_log)
    df.to_csv('outputs/static_stats.csv', index=False)
    print("Success! Baseline simulation complete and forcibly saved to outputs/static_stats.csv")
else:
    print("Error: No data was collected. Make sure your routes.rou.xml is actually spawning cars!")