import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor
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


def mean(arr):
    return arr.mean(axis=0)

def median(arr):
    return np.median(arr,axis=0)

def std(arr):
    return arr.std(axis=0)

def sem(arr):
    return arr.std(axis=0) / np.shape(arr)[0]

def max(arr):
    return arr.max(axis=0)

def min(arr):
    return arr.min(axis=0)



arra = np.zeros(shape=(100,1201))

dec = np.zeros(100)
acc = np.zeros(100)


morans=np.zeros(100)

beliefs = np.zeros(shape = (100,1201))
temp = np.zeros(100)

plt.figure()




for j in [0]:
    outputdir = f"/home/thiemenrug/Desktop/parallel_{j}/"
    for i in range(100):
        outputfolder=outputdir + f"Instance_{i}"

        p = WebotsProcessor(outputfolder,i)
        M = p.read_world_file()[0]
        dec_, acc_ = p.get_dec_time_acc()
        t, estimate = p.compute_average_estimate_f_over_time()

        t,p_= p.compute_average_belief_over_time()
        morans[i] = calculate_morans_I(M)

        temp[i] = estimate[-1]
        beliefs[i,:]  = p_.copy()
        dec[i] = dec_
        acc[i] = acc_

    print(mean(dec))
    print(mean(acc))
    plt.hist2d(morans,temp,bins=50)
plt.colorbar()
plt.show()