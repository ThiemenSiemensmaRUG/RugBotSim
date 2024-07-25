import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor



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

plt.figure()


outputdir = f"/home/thiemenrug/Desktop/parallel_{9}/"

for i in range(1):
    outputfolder=outputdir + f"Instance_{i}"

    p = WebotsProcessor(outputfolder,i)
    x = p.get_intersample_time()



    print(x)

plt.hist(x,bins=400)
plt.show()