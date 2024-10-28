from webots_log_processor import WebotsProcessor
import numpy as np
import matplotlib.pyplot as plt
from utils import *

def get_batch_results(folder,files):
    exps = []
    print(files)
    for file in files:
        exps.append(WebotsProcessor(folder,file,1.33))
    results = concat_experiments(exps)
    return results

def compare(folder):
    Uminfiles = [f"UMIN{i}.csv" for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]]
    Uplusfiles = [f"UPLUS{i}.csv" for i in [1,2,3,4,5,6,7,8,9,10,11,12]]
    Usfiles = [f"US{i}.csv" for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]]
    for i,file in enumerate(Uminfiles):
        x= WebotsProcessor(folder,file,1)
        t,a = x.get_dec_time_acc()
        print(f"{file}: t={round(t)}, a = {round(a,2)}")
    for i,file in enumerate(Uplusfiles):
        x= WebotsProcessor(folder,file,1)
        t,a = x.get_dec_time_acc()
        print(f"{file}: t={round(t)}, a = {round(a,2)}")
    for i,file in enumerate(Usfiles):
        x= WebotsProcessor(folder,file,1)
        t,a = x.get_dec_time_acc()
        print(f"{file}: t={round(t)}, a = {round(a,2)}")
    pass


folder = "/home/thiemenrug/Documents/SI_Journal/Experiments/"

simfolder = "/home/thiemenrug/Documents/SI_Journal/Experiments/"
Uminsim = [f"parallel_0/Instance_{i}/webots_log_{i}.txt" for i in range(1)]
Uplussim = [f"parallel_1/Instance_{i}/webots_log_{i}.txt" for i in range(1)]
Ussim = [f"parallel_2/Instance_{i}/webots_log_{i}.txt" for i in range(1)]

Uminsim = get_batch_results(simfolder,Uminsim)
Uplussim = get_batch_results(simfolder,Uplussim)
Ussim = get_batch_results(simfolder,Ussim)

Uminfiles = [f"UMIN{i}.csv" for i in [1,2,6,7,8,9,15,2,12,13]]
Uplusfiles = [f"UPLUS{i}.csv" for i in [1,2,5,6,7,8,9,10,11,12]]
Usfiles = [f"US{i}.csv" for i in [1,2,4,5,8,9,10,11,12,14]]

Umin = get_batch_results(folder,Uminfiles)
Uplus = get_batch_results(folder,Uplusfiles)
Us = get_batch_results(folder,Usfiles)

plt.figure()
t,p = Umin.compute_average_belief_over_time()
plt.plot(t,p,label ="umin")
t,p = Uplus.compute_average_belief_over_time()
plt.plot(t,p,label ="uplus")
t,p = Us.compute_average_belief_over_time()
plt.plot(t,p,label ="us")
plt.legend()


plt.figure()
t,p = Uminsim.compute_average_belief_over_time()
plt.plot(t,p,label ="umin")
t,p = Uplussim.compute_average_belief_over_time()
plt.plot(t,p,label ="uplus")
t,p = Ussim.compute_average_belief_over_time()
plt.plot(t,p,label ="us")
plt.legend()

plt.show()