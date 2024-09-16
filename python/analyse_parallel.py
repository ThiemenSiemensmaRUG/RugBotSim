import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor

from utils import *



run =10

outputfolder = f"/home/thiemenrug/Desktop/parallel_{run}/"

Umin_exp = [WebotsProcessor(f"{outputfolder}Instance_{i}/",f"webots_log_{i}.txt",.5) for i in range(100)]



Umin_exp = concat_experiments(Umin_exp)

x,y= Umin_exp.get_samples_locations()


plt.figure()
plt.hist2d(x,y,bins = (5,5))
plt.colorbar()

plt.show()


acc = []

beliefs = np.zeros(shape=(100,1201))

outputdir = f"/home/thiemenrug/Desktop/parallel_{run}/"
for i in range(100):
    outputfolder=outputdir + f"Instance_{i}/"
    p = WebotsProcessor(outputfolder,f"/webots_log_{i}.txt",0.5)

    t,ac = p.get_dec_time_acc()
    acc.append(ac)
    t,p_= p.compute_average_belief_over_time()
    beliefs[i,:] = p_

print(np.mean(acc))
plt.plot(t,mean_(beliefs))
plt.show()