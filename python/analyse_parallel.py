import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor

from utils import calculate_morans_I,mean_ 

arra = np.zeros(shape=(100,1201))

dec = np.zeros(100)
acc = np.zeros(100)


morans=np.zeros(100)

beliefs = np.zeros(shape = (100,1201))
temp = np.zeros(100)


linestylz  = ['dashed','dotted','dashdot','--','-.']
instance = 1

plt.figure()
for run in range(1,4):
    outputdir =  f"/home/thiemenrug/Desktop/parallel_{run}/Instance_{instance}/"
    
    p = WebotsProcessor(outputdir,f"/webots_log_{instance}.txt",1.4)
    print(p.fp_percentage,p.fn_percentage)
    t,belief = p.compute_average_belief_over_time()
    
    plt.plot(t,belief,linestyle = linestylz[run-5],label = run)
plt.legend()
plt.show()



# for j in range(5):
#     outputdir = f"/home/thiemenrug/Desktop/parallel_{j}/"
#     for i in range(100):
#         outputfolder=outputdir + f"Instance_{i}/"

#         p = WebotsProcessor(outputfolder,f"/webots_log_{i}.txt")
#         M = p.read_world_file()[0]
#         dec_, acc_ = p.get_dec_time_acc()
#         t, estimate = p.compute_average_estimate_f_over_time()

#         t,p_= p.compute_average_belief_over_time()
#         morans[i] = calculate_morans_I(M)

#         temp[i] = estimate[-1]
#         beliefs[i,:]  = p_.copy()
#         dec[i] = dec_
#         acc[i] = acc_

#     print(mean_(dec))
#     print(mean_(acc))
