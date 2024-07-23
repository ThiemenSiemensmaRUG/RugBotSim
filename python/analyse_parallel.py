import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor

def get_weight_matrix(size):
    W = np.zeros((size*size, size*size))
    for i in range(size):
        for j in range(size):
            index = i * size + j
            if i > 0:
                W[index, index - size] = 1
            if i < size - 1:
                W[index, index + size] = 1
            if j > 0:
                W[index, index - 1] = 1
            if j < size - 1:
                W[index, index + 1] = 1
    return W



# Step 3: Calculate Moran's I
def morans_i(matrix, W):
    n = matrix.size
    x = matrix.flatten()
    mean_x = np.mean(x)
    num = np.sum(W * ((x - mean_x).reshape(-1, 1) * (x - mean_x)))
    den = np.sum((x - mean_x) ** 2)
    W_sum = np.sum(W)
    I = (n / W_sum) * (num / den)
    return I

def mean(arr):
    return arr.mean(axis=0)

def std(arr):
    return arr.std(axis=0)

def sem(arr):
    return arr.std(axis=0) / np.shape(arr)[0]

def max(arr):
    return arr.max(axis=0)

def min(arr):
    return arr.min(axis=0)

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size//2:]


size = 5
W = get_weight_matrix(size)

for feedback in [2]:
    outputdir = f"/home/thiemenrug/Desktop/parallel_{feedback}/"
    acc = []
    scores= []
    ps = np.zeros(shape=(100,1201))
    for i in range(100):
        outputfolder=outputdir + f"Instance_{i}"

        p = WebotsProcessor(outputfolder,i)
        w,w_col = p.read_world_file()
        mat=w

        time,ac= p.get_dec_time_acc()
        acc.append(ac)
        scores.append(morans_i(mat, W))
        

print(acc,scores)
list1 = acc
list2 = scores
# Step 2: Plot the original unsorted lists against each other
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.scatter(list1, list2, color='blue')
plt.title("Unsorted Lists")
plt.xlabel("List 1")
plt.ylabel("List 2")

# Step 3: Sort list1 and apply the same index changes to list2
sorted_indices = sorted(range(len(list1)), key=lambda k: list1[k])
sorted_list1 = [list1[i] for i in sorted_indices]
sorted_list2 = [list2[i] for i in sorted_indices]

# Step 4: Plot the sorted list against the reordered list
plt.subplot(1, 2, 2)
plt.scatter(sorted_list1, sorted_list2, color='red')
plt.title("Sorted List 1 vs Reordered List 2")
plt.xlabel("Sorted List 1")
plt.ylabel("Reordered List 2")

plt.tight_layout()
plt.show()
