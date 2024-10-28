import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor
from utils import *


def get_folder_results(run,len=100,size=5):
    outputfolder = f"/home/thiemenrug/Desktop/parallel_{run}/"
    result_ = []
    for i in range(len):
        try:
            result_.append(WebotsProcessor(outputfolder + f"Instance_{i}/",f"/webots_log_{i}.txt",0.5,size=size))
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
    k=10
    for i in range(8):
        for j in range(4):
            x = get_folder_results(k,batch_size)
            time,acc = x.get_dec_time_acc()
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            k+=1
    plt.figure()
    for i in range(len(usps)):
        plt.plot(etas,resulting_acc[:,i],label =str(round(usps[i]/1000)),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xlabel("$\\eta$")
    plt.ylabel("Accuracy")
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
    run = 50
    for i in range(len(fill_ratios)):
        for j in range(len(methods)):
            x = get_folder_results(run,batch_size)
            time,acc = x.get_dec_time_acc()
            if fill_ratios[i] >.5:
                acc= 1-acc
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            run+=1
    print(run)
    print(resulting_time,"\n",resulting_acc)
    time = resulting_time

    acc = resulting_acc
        
    # Plot for ACC

    plt.figure()
    plt.imshow((time).transpose(), cmap='Greys', aspect='auto',vmin = 300, vmax = 1200)
    plt.colorbar(label='Time [s]')
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.yticks(ticks=np.arange(len(methods)), labels=[str((u)) for u in methods])
    plt.xlabel("$f$")
    plt.ylabel("Feedback")


    plt.figure()
    plt.imshow((acc).transpose(), cmap='Greys', aspect='auto',vmin = 0.5, vmax = 1)
    plt.colorbar(label='Accuracy')
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.yticks(ticks=np.arange(len(methods)), labels=[str((u)) for u in methods])
    plt.xlabel("$f$")
    plt.ylabel("Feedback")



    plt.figure()
    for i in range(len(methods)):
        plt.plot(range(4),acc[:,i],label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.legend(loc='center right', bbox_to_anchor=(1.3,0.5), ncol=1)
    plt.xlabel("$f$")
    plt.ylabel("Accuracy")

    plt.figure()
    for i in range(len(methods)):
        plt.plot(range(4),time[:,i],label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.legend(loc='center right', bbox_to_anchor=(1.3,0.5), ncol=1)
    plt.xlabel("$f$")
    plt.ylabel("Time")
    plt.show()





    return

def plot_multi_robot():
    fill_ratios = [.48,.52]
    n_robots = [10,9,8,7,6,5]
    methods = ["$u^-$","$u^+$","$u^s$"]
    run = 100
    resulting_acc = np.zeros(shape=(2,6,3))
    resulting_time = np.zeros(shape = (2,6,3))
    for fill in range(len(fill_ratios)):
        for n_r in range(len(n_robots)):
            for feedback in range(len(methods)):
                x = get_folder_results(run,batch_size)
                time,acc = x.get_dec_time_acc()
                if fill >.5:
                    acc= 1-acc
                resulting_acc[fill,n_r,feedback] = acc
                resulting_time[fill,n_r,feedback] = time
                run+=1
    
    #select 0 or 1st index for 48 and 52 percent respectively
    time = resulting_time[0,:,:].transpose()

    acc = resulting_acc[0,:,:].transpose()
        
    # Plot for ACC

    plt.figure()
    plt.imshow(np.flip(time,axis=1), cmap='Greys', aspect='auto',vmin = 300, vmax = 1200)
    plt.colorbar(label='Time [s]')
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.yticks(ticks=np.arange(len(methods)), labels=[str((u)) for u in methods])
    plt.xlabel("$N_r$")
    plt.ylabel("Feedback")


    plt.figure()
    plt.imshow(np.flip(acc,axis=1), cmap='Greys', aspect='auto',vmin = 0.5, vmax = 1)
    plt.colorbar(label='Accuracy')
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.yticks(ticks=np.arange(len(methods)), labels=[str((u)) for u in methods])
    plt.xlabel("$N_r$")
    plt.ylabel("Feedback")



    plt.figure()
    for i in range(len(methods)):
        plt.plot(range(6),np.flip(acc[i,:],axis=0),label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='center right', bbox_to_anchor=(1.3,0.5), ncol=1)
    plt.xlabel("$N_r$")
    plt.ylabel("Accuracy")

    plt.figure()
    for i in range(len(methods)):
        plt.plot(range(6),np.flip(time[i,:],axis=0),label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='center right', bbox_to_anchor=(1.3,0.5), ncol=1)
    plt.xlabel("$N_r$")
    plt.ylabel("Time")
    plt.show()

    return


def plot_robustness_analysis():
    M1 = diagonal_matrix()
    M2 = stripe_matrix()
    M3 = block_diagonal_matrix()
    M4 = organized_alternating_matrix()
    M5 = random_matrix()
    Ms = [M1,M2,M3,M4,M5]
    matrices = ["M1","M2","M3","M4","M5"]
    methods = ["$u^-$","$u^+$","$u^s$"]
    run = 150
    resulting_acc = np.zeros(shape=(5,3))
    resulting_time = np.zeros(shape = (5,3))
    entropies = []
    MIs = []
    for m in range(len(matrices)):
        entropies.append(entropy(Ms[m]))
        MIs.append(calculate_morans_I(Ms[m]))
        for feedback in range(len(methods)):
                x = get_folder_results(run,batch_size,size=10)
                time,acc = x.get_dec_time_acc()
                resulting_acc[m,feedback] = acc
                resulting_time[m,feedback] = time
                run+=1
    print(resulting_acc,"\n",resulting_time)


    temp_acc = np.zeros(shape=(3,5,3))
    temp_time = np.zeros(shape=(3,5,3))
    for s in range(len(methods)):
        acc = resulting_acc[:,s]
        time = resulting_time[:,s]
        for m in range(len(matrices)):
            temp_acc[s,m,0] = acc[m]
            temp_acc[s,m,1] = entropies[m]
            temp_acc[s,m,2] = MIs[m]
            temp_time[s,m,0] = time[m]
            temp_time[s,m,1] = entropies[m]
            temp_time[s,m,2] = MIs[m]

    plt.figure()
    
    print(temp_acc)
        




if __name__ == "__main__":

    batch_size = 100
    plot_fill_ratio_result()
