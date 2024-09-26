import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor
from utils import *


def get_folder_results(run,len=100):
    outputfolder = f"/home/thiemenrug/Desktop/parallel_{run}/"
    result_ = []
    for i in range(len):
        try:
            result_.append(WebotsProcessor(outputfolder + f"Instance_{i}/",f"/webots_log_{i}.txt",0.5))
        except:
            print(f"Failure for folder {run} instance {i}")
    results = concat_experiments(result_)
    return results





### plot results for calibration Us
def plot_calibration_us():
    
    etas = [750,1000,1250,1500,1750,2000,2250,2500]
    usps = [1000,2000,3000,4000]
    resulting_acc = np.zeros(shape=(8,4))
    resulting_time = np.zeros(shape = (8,4))
    k=70
    for i in range(8):
        for j in range(4):
            x = get_folder_results(k,100)
            time,acc = x.get_dec_time_acc()
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            k+=1
    plt.figure()
    for i in range(len(usps)):
        plt.plot(etas,resulting_acc[:,i],label =str(round(usps[i]/1000)),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xlabel("$\\eta$")
    plt.ylabel("Accuracy $p$")
    plt.legend(loc='center right', bbox_to_anchor=(1.3,.5), ncol=1,title = "$\kappa$")
    plt.savefig(f"/home/thiemenrug/Documents/PDFs/ANTS2024JournalFigs/CalibrationUs_Accuracy.pdf")
    plt.figure()
    for i in range(len(usps)):
        plt.plot(etas,resulting_time[:,i],label = str(round(usps[i]/1000)),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xlabel("$\\eta$")
    plt.ylabel("Time $[s]$")
    plt.legend(loc='center right', bbox_to_anchor=(1.3,0.5), ncol=1,title = "$\kappa$")
    plt.savefig(f"/home/thiemenrug/Documents/PDFs/ANTS2024JournalFigs/CalibrationUs_Time.pdf")
    
    
    plt.figure()
    plt.imshow(resulting_acc, cmap='Greys', aspect='auto',vmin = 0.675,vmax = 0.775)
    plt.colorbar(label='Accuracy')
    plt.xticks(ticks=np.arange(len(usps)), labels=[str(round(u/1000)) for u in usps])
    plt.yticks(ticks=np.arange(len(etas)), labels=etas)
    plt.xlabel("$\\eta$")
    plt.ylabel("$\\kappa$")

    # Adding text inside the squares for accuracy
    for i in range(len(etas)):
        for j in range(len(usps)):
            plt.text(j, i, f'{resulting_acc[i, j]:.2f}', ha='center', va='center', color='red')

   
    plt.savefig("/home/thiemenrug/Documents/PDFs/ANTS2024JournalFigs/CalibrationUs_Accuracy_Heatmap.pdf")

    # Plot for Time
    plt.figure()
    plt.imshow(resulting_time, cmap='Greys', aspect='auto',vmin = 500, vmax = 1000)
    plt.colorbar(label='Time [s]')
    plt.xticks(ticks=np.arange(len(usps)), labels=[str(round(u/1000)) for u in usps])
    plt.yticks(ticks=np.arange(len(etas)), labels=etas)
    plt.xlabel("$\\eta$")
    plt.ylabel("$\\kappa$")

    # Adding text inside the squares for time
    for i in range(len(etas)):
        for j in range(len(usps)):
            plt.text(j, i, f'{resulting_time[i, j]:.0f}', ha='center', va='center', color='red')


    plt.savefig("/home/thiemenrug/Documents/PDFs/ANTS2024JournalFigs/CalibrationUs_Time_Heatmap.pdf")

    
    
    plt.show()

def plot_fill_ratio_result():
    fill_ratios = [.44,.48,.52,.56]
    methods = ["$u^-$","$u^+$","$u^s$"]
    resulting_acc = np.zeros(shape=(4,3))
    resulting_time = np.zeros(shape = (4,3))
    run = 110
    for i in range(len(fill_ratios)):
        for j in range(len(methods)):
            x = get_folder_results(run,100)
            time,acc = x.get_dec_time_acc()
            if fill_ratios[i] >.5:
                acc= 1-acc
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            run+=1
    print(resulting_time,"\n",resulting_acc)
    return

def plot_multi_robot():


    return







plot_fill_ratio_result()