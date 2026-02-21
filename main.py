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