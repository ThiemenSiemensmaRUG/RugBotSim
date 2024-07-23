import pandas as pd
import numpy as np


class WebotsProcessor:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.data = None
        self._read_file()

    def _read_file(self):
        """Reads the file and parses the data, skipping any junk prints"""
        with open(self.filename, 'r') as file:
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

    def get_intersample_time(self):
        # Get unique robot IDs
        robot_ids = self.data['robot_id'].unique()
        times = []
        # Compute distances, X and Y distances, and directions for each robot
        for robot_id in robot_ids:
            robot_data = self.filter_by_robot_id(robot_id).copy()
            # Compute X and Y distances
            robot_data['time_diff'] = robot_data['time'].diff()
            times.append(robot_data[['time', 'robot_id', 'time_diff']])
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
        for robot_id in robot_ids:
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
        for robot_id in robot_ids:
            robot_data = self.filter_by_robot_id(robot_id).copy()
            # Ensure data is sorted by time
            robot_data = robot_data.sort_values(by='time')
            # Create a new DataFrame with a continuous time range (0 to 1200 seconds, in 1 second steps)
            continuous_time = pd.DataFrame({'time': np.arange(0, 1201)})
            # Merge with the original data to get the continuous time index
            robot_data = pd.merge(continuous_time, robot_data, on='time', how='left')
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
        for robot_id in robot_ids:
            robot_data = self.filter_by_robot_id(robot_id).copy()

            pos.append(robot_data[['time', 'robot_id', 'pos_x','pos_y']])

        sample_data = pd.concat(pos).reset_index(drop=True)
        return sample_data['pos_x'],sample_data['pos_y']



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
        for robot_id in robot_ids:
            robot_data = self.filter_by_robot_id(robot_id).copy()
            
            # Compute X and Y distances
            robot_data['x_distance'] = robot_data['pos_x'].diff()
            robot_data['y_distance'] = robot_data['pos_y'].diff()
            
            # Compute distance (Euclidean)
            robot_data['distance'] = np.sqrt(robot_data['x_distance']**2 + robot_data['y_distance']**2)
            
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
            return distance_data['distance'], x_distance_data['x_distance'], y_distance_data['y_distance'], direction_data['direction']
