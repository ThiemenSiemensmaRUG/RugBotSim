import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from scipy.ndimage import convolve

def apply_box_filter_2d(data, kernel_size=7):
    """
    Apply a 2D box low-pass filter to the data.

    :param data: The 2D data to be filtered (e.g., the mode or mode_curvature).
    :param kernel_size: The size of the square kernel (3x3, 5x5, etc.).
    :return: The smoothed data after applying the box filter.
    """
    # Create a box kernel (uniform averaging filter)
    kernel = np.ones((kernel_size, kernel_size)) / (kernel_size ** 2)
    
    # Apply convolution with the box kernel
    return convolve(data, kernel)

def plot_surface(X,Y,Z):

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surf = ax.plot_surface(X, Y, Z, cmap='viridis')

    # Adding labels
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    # Show the color bar
    plt.colorbar(surf)

def create_grid(df, tolerance):
    xunique = df['x'].unique()
    yunique = df['y'].unique()
    x_min, x_max = df['x'].min(), df['x'].max()
    y_min, y_max = df['y'].min(), df['y'].max()

    step_x = int((x_max - x_min) / tolerance)
    step_y = int((y_max - y_min) / tolerance)
    x_grid = np.linspace(x_min, x_max,step_x+1)
    y_grid = np.linspace(y_min, y_max, step_y+1)
    gridX, gridY = np.meshgrid(x_grid, y_grid)
    return gridX, gridY




class WebotsLogProcessor:
    def __init__(self, run, instance):
        self.run = run
        self.instance = instance
        self.file = f"jobfiles/Run_{self.run}/Instance_{self.instance}/webots_log_{self.instance}.txt"
        self.df = None
        self.X = None
        self.Y = None
        self.mode = None
        self.mode_curvature = None
    
    def is_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def read_and_process_data(self):
        # Read the file
        with open(self.file, 'r') as file:
            lines = file.readlines()
        
        # Parse lines containing "crash"
        crash_lines = [line for line in lines if "crash" in line]
        if len(crash_lines) != 0:
            raise RuntimeError(f"Crash detected in log file. Exiting the script. Crash details: {crash_lines}")
        

        # Filter data lines with at least 3 commas and valid numbers
        data_lines = [
            line.strip() for line in lines
            if line.count(',') >= 3 and all(self.is_number(value) for value in line.strip().split(','))
        ]
        
        # Convert the data lines to a list of floats
        data_list = [list(map(float, line.split(','))) for line in data_lines]
        
        # Create DataFrame
        self.df = pd.DataFrame(data_list, columns=['t', 'rov_num', 'x', 'y', 'z'])
        
        # Drop NaN values
        self.df = self.df.dropna()
        self.df = self.df[self.df['z'] != 0.0]
    

    def plot_density(self, bins = 10):
        plt.figure(figsize=(8, 6))
        plt.hist2d(self.df['x'], self.df['y'], bins=bins)
        plt.colorbar(label='Density')
        plt.xlabel('X Label')
        plt.ylabel('Y Label')
        plt.title('Point Density')

    def compute_mode_shape(self, accuracy = 100):
        # Create a grid for x, y values

        points = points = self.df[['x', 'y']].values  # Array of (x, y) points
        values = self.df['z'].values  # Corresponding displacement magnitudes
        # Create a regular grid
        x_min, x_max = 0, 1000
        y_min, y_max = 0, 1000
        x_grid = np.linspace(x_min, x_max, accuracy)
        y_grid = np.linspace(y_min, y_max, accuracy)
        self.X, self.Y = np.meshgrid(x_grid, y_grid)
       
        # Interpolate the displacement magnitude onto the grid
        self.mode = griddata(points, values, (self.X, self.Y), method='linear',fill_value=0)
  
        #self.mode = gaussian_filter(self.mode, sigma=2)
        self.mode = apply_box_filter_2d(self.mode, 10)
        Z_xx = np.gradient(np.gradient(self.mode, axis=1), axis=1)
        Z_yy = np.gradient(np.gradient(self.mode, axis=0), axis=0)
        self.mode_curvature = Z_xx + Z_yy
        self.mode_curvature = apply_box_filter_2d(self.mode_curvature, 10)
        
        return self.mode , self.mode_curvature
  