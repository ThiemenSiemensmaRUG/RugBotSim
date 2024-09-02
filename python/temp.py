
import numpy as np
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


M1 = np.array([[1,1,0,0,0],[1,1,1,0,0],[0,1,1,1,0],[0,0,1,1,1],[0,0,0,0,1]])#diagonal
M2 = np.array([[1,1,1,1,1],[1,1,1,1,1],[1,1,0,0,0],[0,0,0,0,0],[0,0,0,0,0]])#stripe
M3 = np.array([[0,0,1,1,1],[0,0,1,1,1],[0,0,1,1,1],[1,0,0,0,0],[1,1,0,0,0]])#block diagonal
M4 = np.array([[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0]])#organized
M5 = np.array([[0,0,0,1,1],[0,1,1,0,0],[0,0,1,1,1],[0,1,1,0,0],[1,1,0,1,0]])#random

print(calculate_morans_I(M1))
print(calculate_morans_I(M2))
print(calculate_morans_I(M3))
print(calculate_morans_I(M4))
print(calculate_morans_I(M5))