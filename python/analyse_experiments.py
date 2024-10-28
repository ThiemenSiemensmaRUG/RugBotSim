from webots_log_processor import WebotsProcessor
import numpy as np
import matplotlib.pyplot as plt
from utils import *

def get_batch_results(folder,files):
    exps = []

    for file in files:
        exps.append(WebotsProcessor(folder,file,1.33,time=1001))
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


folder = "/home/thiemenrug/Documents/SI_Journal/Real/"

simfolder = "/home/thiemenrug/Documents/SI_Journal/Real/"
Uminsim = [f"parallel_0/Instance_{i}/webots_log_{i}.txt" for i in range(10)]
Uplussim = [f"parallel_1/Instance_{i}/webots_log_{i}.txt" for i in range(10)]
Ussim = [f"parallel_2/Instance_{i}/webots_log_{i}.txt" for i in range(10)]

Uminsim = get_batch_results(simfolder,Uminsim)
Uplussim = get_batch_results(simfolder,Uplussim)
Ussim = get_batch_results(simfolder,Ussim)

Uminfiles = [f"UMIN{i}.csv" for i in range(1,11)]
Uplusfiles = [f"UPLUS{i}.csv" for i in range(1,11)]
Usfiles = [f"US{i}.csv" for i in range(1,11)]

Umin = get_batch_results(folder,Uminfiles)
Uplus = get_batch_results(folder,Uplusfiles)
Us = get_batch_results(folder,Usfiles)

bplot_acc = []
bplot_time = []

plt.figure()
t,p = Umin.compute_average_belief_over_time()
df_t, df_acc = Umin.get_dec_time_acc_robots()
bplot_acc.append(df_acc)
bplot_time.append(df_t)
plt.plot(t,p,label ="$u^-$",linestyle=linestyles_[1],color = "darkgray")

t,p = Uplus.compute_average_belief_over_time()
df_t, df_acc = Uplus.get_dec_time_acc_robots()
bplot_acc.append(df_acc)
bplot_time.append(df_t)
plt.plot(t,p,label ="$u^+$",linestyle=linestyles_[2],color = "black")

t,p = Us.compute_average_belief_over_time()
df_t, df_acc = Us.get_dec_time_acc_robots()
bplot_acc.append(df_acc)
bplot_time.append(df_t)
plt.plot(t,p,label ="$u^s$",linestyle=linestyles_[3],color ="dimgray")

plt.xlabel("Time [s]")
plt.ylabel("Belief")
plt.legend(loc='upper right', bbox_to_anchor=(1.0,1.3), ncol=3)
plt.tight_layout(pad=0.05)



bplot_acc_sim = []
bplot_time_sim = []

plt.figure()
t,p = Uminsim.compute_average_belief_over_time()
df_t, df_acc = Uminsim.get_dec_time_acc_robots()
bplot_acc_sim.append(df_acc)
bplot_time_sim.append(df_t)
plt.plot(t,p,label ="$u^-$",linestyle=linestyles_[1],color = "darkgray")

t,p = Uplussim.compute_average_belief_over_time()
df_t, df_acc = Uplussim.get_dec_time_acc_robots()
bplot_acc_sim.append(df_acc)
bplot_time_sim.append(df_t)
plt.plot(t,p,label ="$u^+$",linestyle=linestyles_[2],color = "black")

t,p = Ussim.compute_average_belief_over_time()
df_t, df_acc = Ussim.get_dec_time_acc_robots()
bplot_acc_sim.append(df_acc)
bplot_time_sim.append(df_t)
plt.plot(t,p,label ="$u^s$",linestyle=linestyles_[3],color ="dimgray")

plt.xlabel("Time [s]")
plt.ylabel("Belief")
plt.legend(loc='upper right', bbox_to_anchor=(1.0,1.3), ncol=3)
plt.tight_layout(pad=0.05)


plt.figure()
plt.ylim([-0.1,1.1])
plt.ylabel("Time [s]")
poss= [0.75, 1.25,  2.25,2.75, 3.75, 4.25]
box = plt.boxplot([bplot_acc[0],bplot_acc_sim[0],bplot_acc[1],bplot_acc_sim[1],bplot_acc[2],bplot_acc_sim[2]],positions = poss, widths=0.4, patch_artist=True)
colors_sim = 'lightgray'
colors_real = 'dimgray'
# Define colors for simulation and real
for i, patch in enumerate(box['boxes']):
    if i % 2 == 0:  # Sim data (even indices)
        patch.set_facecolor(colors_sim)
    else:  # Real data (odd indices)
        patch.set_facecolor(colors_real)

plt.xticks([1, 2.5, 4], ['$u^-$', '$u^+$', '$u^s$'])
plt.legend([box["boxes"][0], box["boxes"][1]], ['Sim (left)', 'Real (right)'], loc='upper right', bbox_to_anchor=(1.0,1.3), ncol=2)
plt.tight_layout(pad=0.05)

plt.figure()
plt.ylim([400,1200])
plt.ylabel("Time [s]")
poss= [0.75, 1.25,  2.25,2.75, 3.75, 4.25]
box = plt.boxplot([bplot_time[0],bplot_time_sim[0],bplot_time[1],bplot_time_sim[1],bplot_time[2],bplot_time_sim[2]],positions = poss, widths=0.4, patch_artist=True)
colors_sim = 'lightgray'
colors_real = 'dimgray'
# Define colors for simulation and real
for i, patch in enumerate(box['boxes']):
    if i % 2 == 0:  # Sim data (even indices)
        patch.set_facecolor(colors_sim)
    else:  # Real data (odd indices)
        patch.set_facecolor(colors_real)

plt.xticks([1, 2.5, 4], ['$u^-$', '$u^+$', '$u^s$'])
plt.legend([box["boxes"][0], box["boxes"][1]], ['Sim (left)', 'Real (right)'], loc='upper right', bbox_to_anchor=(1.0,1.3), ncol=2)
plt.tight_layout(pad=0.05)
plt.show()
