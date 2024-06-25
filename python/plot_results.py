import pandas as pd
import matplotlib.pyplot as plt

# Step 3: Read the data into a pandas DataFrame
df = pd.read_csv('python/data_rov.txt', names=['time', 'robot_id', 'value'])

# Step 4: Plot the data
fig, ax = plt.subplots(figsize=(10, 6))

# Loop through each robot_id and plot its data
for robot_id, group in df.groupby('robot_id'):
    ax.plot(group['time'], group['value'], marker='o', linestyle='-', label=f'Robot {robot_id}')

# Calculate the mean value for each time step
mean_values = df.groupby('time')['value'].mean()

# Plot the mean values
ax.plot(mean_values.index, mean_values, marker='x', linestyle='--', color='black', label='Mean')

ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.set_ylim([0, 15])
ax.set_title('Plotted Values over Time for Robots')
ax.legend()

plt.grid(True)
plt.tight_layout()
plt.show()
