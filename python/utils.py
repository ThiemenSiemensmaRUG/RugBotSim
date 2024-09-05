import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# Set figure size in inches for optimal DPI
scaling = .5
plt.rcParams['figure.figsize'] = [6.4 * scaling, 4.8 * scaling]  # Standard figure size, can be adjusted as needed
plt.rcParams['figure.dpi'] = 300  # High resolution (300 DPI)

# Font settings
plt.rcParams['font.family'] = 'serif'  # Use a serif font like Times New Roman
plt.rcParams['font.size'] = 10  # Adjust according to journal guidelines, typically 10-12pt
plt.rcParams['axes.labelsize'] = 10  # Label size
plt.rcParams['axes.titlesize'] = 12  # Title size, typically slightly larger than labels
plt.rcParams['xtick.labelsize'] = 8  # X-axis tick label size
plt.rcParams['ytick.labelsize'] = 8  # Y-axis tick label size
plt.rcParams['legend.fontsize'] = 8  # Legend font size

# Line and marker styles
plt.rcParams['lines.linewidth'] = 1.5  # Line width for better visibility
plt.rcParams['lines.markersize'] = 6  # Marker size

# Color cycle (Springer tends to favor simple, distinct colors)
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['b', 'g', 'r', 'c', 'm', 'y', 'k'])

# Grid settings (optional)
plt.rcParams['grid.linestyle'] = '--'  # Dashed grid lines
plt.rcParams['grid.alpha'] = 0.7  # Slightly transparent

# Spacing and layout
plt.rcParams['figure.autolayout'] = True  # Automatically adjust layout to prevent overlap

# Save as a high-resolution image for publication

def calculate_morans_I(matrix):
    # Number of rows and columns in the matrix
    n, m = matrix.shape
    
    # Calculate the mean of the matrix values
    mean_value = np.mean(matrix)
    
    # Initialize numerator and denominator for Moran's I calculation
    numerator = 0.0
    denominator = 0.0
    
    # Total number of cells
    N = n * m
    
    # Define adjacency matrix and weight
    W = 0
    weight_sum = 0
    
    for i in range(n):
        for j in range(m):
            # For each cell, compare it with its neighbors (up, down, left, right)
            for (ni, nj) in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
                if 0 <= ni < n and 0 <= nj < m:
                    # Add the weight (here, all neighbors have equal weight 1)
                    W += 1
                    
                    # Calculate the product of deviations
                    numerator += (matrix[i, j] - mean_value) * (matrix[ni, nj] - mean_value)
                    weight_sum += 1
    
            # Calculate the sum of squared deviations for the denominator
            denominator += (matrix[i, j] - mean_value) ** 2
    
    # Calculate Moran's I
    morans_I = (N / W) * (numerator / denominator)
    
    return morans_I


def mean_(arr):
    return arr.mean(axis=0)

def median_(arr):
    return np.median(arr,axis=0)

def std_(arr):
    return arr.std(axis=0)

def sem_(arr):
    return arr.std(axis=0) / np.shape(arr)[0]

def max_(arr):
    return arr.max(axis=0)

def min_(arr):
    return arr.min(axis=0)

def create_one_array(_list):
    new_array = np.concatenate(_list,axis=0)
    return new_array


def fit_normal(data):
    # Estimate the parameters of the normal distribution
    mu = np.mean(data)
    sigma = np.std(data, ddof=0)  # Population standard deviation
    
    # You can return the parameters for further use
    return mu, sigma

def plot_fit(data):
    # Fit the normal distribution
    mu, sigma = fit_normal(data)
    
    # Generate a range of values
    x = np.linspace(min(data), max(data), 100)
    
    # Get the probability density function (PDF) for the fitted normal distribution
    pdf = stats.norm.pdf(x, mu, sigma)
    
    # Plot the histogram of the data
    plt.hist(data, bins=30, density=True, alpha=0.6, color='g')
    
    # Plot the fitted normal distribution
    plt.plot(x, pdf, 'k', linewidth=2)
    plt.title(f'Fit Results: mu = {mu:.2f}, sigma = {sigma:.2f}')
    plt.show()