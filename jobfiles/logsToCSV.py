"""
This script reads the log file from the Webots simulation,
extracts the collected data from the robots, and saves it
to a CSV file.
"""

import pandas as pd

log_path = 'Run_1/Instance_1/webots_log_1.txt'
export_path = 'robot_data.csv'
mode = 1  # Currently useless as mode_num is always 1 by the sampling algorithm

with open(log_path, 'r') as file:
    lines = file.readlines()

# Initialize variables
start_collecting = False
collected_lines = []
robot_data = {'x': [], 'y': [], 'u3': [], 'mode_num': []}

# Process each line in the log file
for line in lines:
    if line.startswith("29,0,"):
        start_collecting = True
    if "INFO: cpp_supervisor: Terminating." in line:
        break
    if start_collecting:
        collected_lines.append(line)

# Parse the collected lines
for line in collected_lines:
    parts = line.strip().split(',')
    x = float(parts[-4])
    y = float(parts[-3])
    u3 = float(parts[-2])
    mode_num = round(float(parts[-1]))
    
    robot_data['x'].append(x)
    robot_data['y'].append(y)
    robot_data['u3'].append(u3)
    robot_data['mode_num'].append(mode_num)

# Transform to dataframe and apply mode
robot_data = pd.DataFrame(robot_data)
robot_data = robot_data[robot_data['mode_num'] == mode]

# Save the data to a CSV file
robot_data.to_csv(export_path, index=False)
