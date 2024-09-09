import pandas as pd
import numpy as np


class WebotsProcessor:
    def __init__(self, folder,filename,threshold = None, grid = np.array([])) -> None:
   
        self.world_file = folder + filename
        self.folder = folder
        self.data = None
        self.threshold = threshold
        if grid.shape[0] == 0:
            self.grid = np.array([
                    [0, 1, 0, 1, 0],  # Row corresponding to y=1.0 to y=0.8
                    [1, 0, 0, 1, 0],  # Row corresponding to y=0.8 to y=0.6
                    [1, 0, 1, 0, 1],  # Row corresponding to y=0.6 to y=0.4
                    [0, 1, 1, 0, 1],  # Row corresponding to y=0.4 to y=0.2
                    [1, 0, 0, 1, 0]   # Row corresponding to y=0.2 to y=0.0
                ])
        else:
            self.grid = grid
 
        if "webots" in str(filename):
            self._read_file()

        else:
            self._read_exp_file()
        
        

    def _read_exp_file(self):
        self.data = pd.read_csv(self.world_file)
        # Adding the 'has_none' column
        self.data['print_bool'] = self.data.isnull().any(axis=1).__invert__()
        self.data =self.data.rename(columns={'Timestamp':'time', 
                                  'ROV Number': 'robot_id',
                                  'X Meter':"pos_x",
                                  "Y Meter":"pos_y",
                                  "Energy":"measurement",
                                  "Alpha":"beta_alpha",
                                  "Beta":"beta_beta",
                                  "Belief":"beta_belief",
                                  "Swarm Send":"sends",
                                  "Swarm Recv":"recvs",
                                  "Collision Time":"ca_time",
                                  "Sense Time":"sample_time"})

        self.data = self.data[self.data['print_bool'] == 1]
        
        self.add_labels()
        self.add_onboard_values()
        self.i_data = self.interpolate_data()
        return

    def _read_file(self):
        """Reads the file and parses the data, skipping any junk prints"""
        with open(self.world_file, 'r') as file:
            lines = file.readlines()
        
        # Parse data lines with at least 10 commas
        data_lines = [line for line in lines if line.count(',') >= 10]
        data_list = [list(map(float, line.split(','))) for line in data_lines]
        
        # Assuming the column names based on the provided data structure
        columns = [
            'print_bool', 'time', 'robot_id', 'sample', 'message', 'beta_belief', 
            'beta_alpha', 'beta_beta', 'sends', 'recvs', 'beta_mean', 
            'beta_onboard_mean', 'pos_x', 'pos_y', 'rw_time', 'ca_time', 
            'sample_time', 'decision_time', 'd_f'
        ]
        
        self.data = pd.DataFrame(data_list, columns=columns)
        self.i_data = self.interpolate_data()
        
    def add_onboard_values(self):
        self.data['beta_onboard'] = (self.data['label'] == 0).cumsum()
        self.data['alpha_onboard'] = (self.data['label'] == 1).cumsum()
        self.data['beta_onboard_mean'] = (self.data['alpha_onboard'] / (self.data['alpha_onboard']+self.data['beta_onboard']))

    def read_world_file(self):
        with open(self.folder + "world.txt", 'r') as file:
            lines = file.readlines()
        
        entries = []
        for line in lines:
            if ',' in line:
                row, col = map(int, line.split(','))
                entries.append((row, col))
        # Initialize a 5x5 matrix filled with zeros
        matrix = np.ones((5, 5), dtype=int)

        # Fill the matrix with the given entries
        for (row, col) in entries:
            matrix[row, col] = 0
        
        return matrix, matrix.reshape(1,25)

    def get_summary(self):
        """Returns a summary of the DataFrame"""
        return self.data.describe()

    def filter_by_robot_id(self, robot_id):
        """Filters the data by robot_id"""
        return self.data[self.data['robot_id'] == robot_id]

    def compute_mean_beliefs(self):
        """Computes the mean of beta beliefs for each robot"""
        return self.data.groupby('robot_id')['beta_belief'].mean()
    
    def get_data(self):
        """Returns the processed data"""
        return self.data

    def get_state_times(self):
        robot_ids = self.data['robot_id'].unique()
        
        def accumulate_values(df):
            for col in ['sample_time', 'ca_time']:
                # Compute the time difference for the given column
                df[f'{col}_diff'] = df[col].diff()
                # Identify reset points where the time difference is negative
                reset_points = df[f'{col}_diff'] < 0
                df['temp'] = 65000
                # Adjust the differences by resetting on negative time jumps
                df[f'{col}_diff'] = df[f'{col}_diff'] + df['temp'] * reset_points.astype(int)
                # Calculate cumulative sum for adjusted times
                df[col] = df[f'{col}_diff'].cumsum()
                df[f'{col}_diff'] = df[col].diff()
            return df

        ca_time = []
        sense_time=[]
        ca_per_sample = []
        for robot_id in np.sort(robot_ids):
            robot_data = self.filter_by_robot_id(robot_id).copy()
            

            # Apply the accumulation function
            robot_data = accumulate_values(robot_data)

            # Add to result list or handle the data further
            ca_time.append(robot_data['ca_time'].iloc[-1])
            sense_time.append(robot_data['sample_time'].iloc[-1])
            
            ca_per_sample.append(np.array(robot_data.dropna()['ca_time_diff']))

        
        # Return processed data, or you could aggregate results if needed
        return ca_time,sense_time,ca_per_sample


    def get_intersample_time(self):
        # Get unique robot IDs
        robot_ids = self.data['robot_id'].unique()
        times = []
        # Compute distances, X and Y distances, and directions for each robot

        for robot_id in np.sort(robot_ids):
            robot_data = self.filter_by_robot_id(robot_id).copy()
            # Compute X and Y distances
            robot_data['time_diff'] = robot_data['time'].diff()
            times.append(robot_data[['time', 'robot_id', 'time_diff']].iloc[:-1])
        all_times =pd.concat(times).reset_index(drop=True).dropna()
 
        return all_times['time_diff']

    def _add_d_f_indicator(self):
        """Adds a binary indicator column for d_f"""
        self.data['d_f_indicator'] = np.where(self.data['d_f'].astype(float).isin([0, 1]), 1, 0)
        

    def get_dec_time_acc(self):
        self._add_d_f_indicator()

        robot_ids = self.data['robot_id'].unique()
        decision_times = []
        accuracies = []
        for robot_id in np.sort(robot_ids):
            robot_data = self.filter_by_robot_id(robot_id).copy()
            robot_data.at[robot_data.index[-1], 'd_f_indicator'] = 1

            index = (robot_data['d_f_indicator'] == 1.0).argmax()
            decision_times.append(robot_data['time'].iloc[index])
            accuracies.append(robot_data['beta_belief'].iloc[index])
        
        return np.array(decision_times).mean(), np.array(accuracies).mean()



    def interpolate_data(self):

        """Interpolates the data per robot per second, ensuring time range is from 0 to 1200 seconds"""
        # Initialize a list to hold interpolated data for each robot
        interpolated_data = []
        # Get unique robot IDs
        robot_ids = self.data['robot_id'].unique()
        # Interpolate data for each robot
        for robot_id in np.sort(robot_ids):
            robot_data = self.filter_by_robot_id(robot_id).copy()
            # Ensure data is sorted by time
            
            robot_data = robot_data.sort_values(by='time')
            # Create a new DataFrame with a continuous time range (0 to 1200 seconds, in 1 second steps)
         
            continuous_time = pd.DataFrame({'time': np.arange(0, 1201)}).astype(float)
            # Merge with the original data to get the continuous time index
            robot_data = pd.merge_asof(continuous_time.astype(float), robot_data.astype(float), left_on='time', right_on='time', direction='nearest')
            #robot_data = pd.merge(continuous_time.astype(float), robot_data.astype(float), on='time', how='left')
            # Interpolate missing values
            robot_data = robot_data.interpolate(method='linear')
            # Fill remaining NaN values if any (e.g., if data doesn't start from 0)
            robot_data = robot_data.bfill().ffill()
            # Add the interpolated data to the list
            interpolated_data.append(robot_data)
        
        # Concatenate all interpolated data into a single DataFrame
        return pd.concat(interpolated_data).reset_index(drop=True)

    def compute_average_belief_over_time(self):
        """Computes the average means of beta beliefs over robots for each time step"""
        # Group by time and compute the mean of beta beliefs for each time step across all robots
        average_means = self.i_data.groupby('time')['beta_belief'].mean().reset_index()
        return np.array(average_means['time']),np.array(average_means['beta_belief'])
    
    def compute_average_estimate_f_over_time(self):
        """Computes the average means of beta beliefs over robots for each time step"""
        # Group by time and compute the mean of beta beliefs for each time step across all robots
        average_means = self.i_data.groupby('time')['beta_onboard_mean'].mean().reset_index()
        return np.array(average_means['time']),np.array(average_means['beta_onboard_mean'])
    
    def get_samples(self):
        vib = self.data[self.data['true_label'] ==1]
        nonvib= self.data[self.data['true_label']==0]
        return vib['measurement'],nonvib['measurement']

    def compute_std_beliefs_over_time(self):
        """Computes the average means of beta beliefs over robots for each time step"""
        # Group by time and compute the std of beta beliefs for each time step across all robots
        average_means = self.i_data.groupby('time')['beta_belief'].std().reset_index()
        return np.array(average_means['time']),np.array(average_means['beta_belief'])

    def get_samples_locations(self):
        # Get unique robot IDs
        robot_ids = self.data['robot_id'].unique()
        pos = []

        # Compute distances, X and Y distances, and directions for each robot
        for robot_id in np.sort(robot_ids):
            robot_data = self.filter_by_robot_id(robot_id).copy()

            pos.append(robot_data[['time', 'robot_id', 'pos_x','pos_y']])

        sample_data = pd.concat(pos).reset_index(drop=True)
        return sample_data['pos_x'],sample_data['pos_y']


    def add_labels(self):
        """
        Labels points based on their position in the 5x5 grid. Add FP FN labels

        :param df: DataFrame with 'x' and 'y' columns representing points in the grid.
        :return: DataFrame with an additional 'label' column.
        """
        def get_label(x, y):
            # Calculate grid indices based on the x, y coordinates
            grid_x = min(int(x // 0.2), 4)  # Ensure max index is 4 (x=1 is the last column)
            grid_y = min(4 - int(y // 0.2), 4)  # Ensure y=1 is the first row and y=0 is the last row

            # Return the label based on the grid matrix
            return self.grid[grid_y][grid_x]

        # Apply the get_label function to each row in the DataFrame
        self.data['true_label'] = self.data.apply(lambda row: get_label(row['pos_x'], row['pos_y']), axis=1)
        self.data['label'] = self.data['measurement'].apply(lambda x: 1 if x > self.threshold else 0)

        # Add a column for False Positives (FP)
        self.data['FP'] = (self.data['label'] == 0) & (self.data['label'] != self.data['true_label'])

        # Add a column for False Negatives (FN)
        self.data['FN'] = (self.data['label'] == 1) & (self.data['label'] != self.data['true_label'])
   
        # Calculate the number of False Positives (FP)
        fp_count = self.data['FP'].sum()

        # Calculate the number of False Negatives (FN)
        fn_count = self.data['FN'].sum()

        # Total number of samples
        total_count = self.data.shape[0]

        # Calculate the percentages
        self.fp_percentage = (fp_count / total_count) * 100
        self.fn_percentage = (fn_count / total_count) * 100
        self.tn_percentage = ((fp_count + fn_count)/ total_count) * 100

        # Print the percentages
        # print(f"Percentage of False Positives (FP)  : {self.fp_percentage:.2f}%")
        # print(f"Percentage of False Negatives (FN)  : {self.fn_percentage:.2f}%")
        # print(f"Percentage of Total Falses (FN/FP)  : {self.tn_percentage:.2f}%")
        self.data['error'] = (self.data['label'] != self.data['true_label'])

    

    def compute_distances_and_directions(self,return_df = False):
        """Computes the distance, X and Y distances, and direction between consecutive samples for each robot"""
        # Initialize lists to hold distances, X distances, Y distances, and directions for each robot
        distances = []
        x_distances = []
        y_distances = []
        directions = []

        # Get unique robot IDs
        robot_ids = self.data['robot_id'].unique()
      

        # Compute distances, X and Y distances, and directions for each robot
        for robot_id in np.sort(robot_ids):
            
            robot_data = self.filter_by_robot_id(robot_id).copy()
            robot_data = robot_data.sort_values(by='time')
            
            # Compute X and Y distances
            robot_data['x_distance'] = robot_data['pos_x'].diff()
            robot_data['y_distance'] = robot_data['pos_y'].diff()
            
            # Compute distance (Euclidean)
            robot_data['distance'] = np.sqrt(robot_data['x_distance']**2 + robot_data['y_distance']**2)
            robot_data = robot_data[robot_data['distance']!=0]
            # Compute direction (angle in degrees)
            robot_data['direction'] = np.degrees(np.arctan2(
                robot_data['y_distance'], robot_data['x_distance']
            ))
            
            # Fix direction values to be in the range [0, 360) degrees
            robot_data['direction'] = robot_data['direction'] % 360
            
            # Add distances, X and Y distances, and directions to the lists
            distances.append(robot_data[['time', 'robot_id', 'distance']])
            x_distances.append(robot_data[['time', 'robot_id', 'x_distance']])
            y_distances.append(robot_data[['time', 'robot_id', 'y_distance']])
            directions.append(robot_data[['time', 'robot_id', 'direction']])
        
        # Concatenate all distances, X and Y distances, and directions into single DataFrames
        distance_data = pd.concat(distances).reset_index(drop=True)
        x_distance_data = pd.concat(x_distances).reset_index(drop=True)
        y_distance_data = pd.concat(y_distances).reset_index(drop=True)
        direction_data = pd.concat(directions).reset_index(drop=True)
        

        if return_df:
            return distance_data, x_distance_data, y_distance_data, direction_data
        else:
            return distance_data['distance'].dropna(), x_distance_data['x_distance'].dropna(), y_distance_data['y_distance'].dropna(), direction_data['direction'].dropna()




