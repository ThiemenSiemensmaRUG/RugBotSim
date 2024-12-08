import pandas as pd
import matplotlib.pyplot as plt
import numpy  as np
# Function to validate each row
def is_valid_row(row):
    try:
        # Check if all columns have the expected number of elements and types
        if len(row) < 5:
            return False
        # Convert each element to the expected type
        for i in range(len(row)):
            row[i] = float(row[i])

        
        return True
    except ValueError:
        return False


class analysis():
    def __init__(self,filename) -> None:
        self.filename = filename


    def read_data(self):
        column_names = ['time', 'rov_num', 'value', 'posx', 'posy', 'alpha', 'beta','count']

        # Read and filter the data
        valid_rows = []
        with open(self.filename, 'r') as file:
            for line in file:
                row = line.strip().split(',')
                if is_valid_row(row):
                    valid_rows.append(row)

        # Create DataFrame from valid rows
        self.data = pd.DataFrame(valid_rows, columns=column_names).dropna()
        self.data = self.data[['time','rov_num','value','count']]

        
        temp  = (self.data.groupby(['time'])['value'].mean().reset_index())

        temp= temp.sort_values(by = 'time')
        self.mean = temp['value']
        self.time = temp['time']
        temp = (self.data.groupby(['time'])['value'].std().reset_index())

        temp= temp.sort_values(by = 'time')
        self.std = temp['value']

        temp = (self.data.groupby(['time'])['count'].mean().reset_index())

        temp= temp.sort_values(by = 'time')
        self.count = temp['count']
        
        
# Plot mean value over time
labels = ["No filter","Slow filter","Faster filter 6 robots","Fast filter 2 robots","Fast fitler high learning rate"]
plt.figure(figsize=(12, 6))
i=0
outputfolder= "jobfiles/Run_1/"
for file in [1]:
    filename = outputfolder+ "Instance_" + str(file) +f"/webots_log_{file}.txt"
    x = analysis(filename)
    x.read_data()
    plt.semilogy(x.time,abs((x.std)),label=labels[i])
    del x
    i+=1

plt.xlabel("Time")
plt.title("Target value = 1.77")
plt.ylabel("Error")
plt.legend()
plt.show()