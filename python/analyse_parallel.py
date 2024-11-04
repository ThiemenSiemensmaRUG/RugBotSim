import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor
from utils import *

plt.rcParams.update({
    "axes.labelsize": 10,  # Label font size
    "axes.titlesize": 10,  # Title font size
    "legend.fontsize": 7.5,  # Legend font size
    "xtick.labelsize": 10,  # X-axis tick font size
    "ytick.labelsize": 10,  # Y-axis tick font size
    "lines.linewidth": 1.0,  # Line width
    "lines.markersize": 3,  # Marker size (adjusted for better visibility)
})


c_1 = ["Black", "Red", "Green"]

def plot_measurements(x_):
    plt.figure()
    plt.scatter(x_.data["pos_x"], x_.data["pos_y"], s=5, c=x_.data['measurement'])
    plt.colorbar()
    plt.clim(vmin =0,vmax = 4)
    plt.tight_layout()
    plt.show()

def get_folder_results(run,len=100,size=5):
    outputfolder = f"/home/thiemenrug/Documents/OutputDir/JournalSI/data/{run}/"
    
    result_ = []
    acc, time = [],[]
    for i in range(len):
        try:
            temp_obj = WebotsProcessor(outputfolder + f"Instance_{i}/",f"/webots_log_{i}.txt",0.5,size=size)
            if temp_obj.valid == False:
                print("continuing....")
                continue
            time_temp,acc_temp = temp_obj.get_dec_time_acc()
            acc.append(acc_temp)
            time.append(time_temp)
            result_.append(temp_obj)
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
            run_ = f"/Cal_Us/parallel_{k}"
            x = get_folder_results(run_,batch_size)

            time,acc = x.get_dec_time_acc()
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            k+=1
    plt.figure()
    for i in range(len(usps)):
        t = (round(usps[i]/1000))
        plt.plot(etas,resulting_acc[:,i],label = r"$u^s|_{k=" + str(t) + r"}$",color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.axhline(0.72478767,label = "$u^-$",color = 'red',linestyle = '--')
    plt.axhline(0.72807469,label = "$u^+$",color = 'blue',linestyle = '-.')
    plt.xlabel("$\\eta$")
    plt.ylabel("Accuracy")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.325), ncol=3)
    plt.tight_layout(pad = 0.05)
    plt.savefig(f"/home/thiemenrug/Documents/OutputDir/JournalSI/figures/CalibrationUs_Accuracy.pdf")

    plt.figure()
    for i in range(len(usps)):
        t = (round(usps[i]/1000))
        plt.plot(etas,resulting_time[:,i], label = r"$u^s|_{k=" + str(t) + r"}$" ,color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.axhline(901.72719192,label = "$u^-$",color = 'red',linestyle = '--')
    plt.axhline(891.42513131,label = "$u^+$",color = 'blue',linestyle = '-.')
    plt.xlabel("$\\eta$")
    plt.ylabel("Time $[s]$")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.325), ncol=3)
    plt.tight_layout(pad = 0.05)
    plt.savefig(f"/home/thiemenrug/Documents/OutputDir/JournalSI/figures/CalibrationUs_Time.pdf")
    
    
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
    plt.savefig("/home/thiemenrug/Documents/OutputDir/JournalSI/figures/CalibrationUs_Accuracy_Heatmap.pdf")

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


    plt.savefig("/home/thiemenrug/Documents/OutputDir/JournalSI/figures/CalibrationUs_Time_Heatmap.pdf")

    
    
    plt.show()

def plot_fill_ratio_result():
    fill_ratios = [.44,.48,.52,.56]
    methods = ["$u^-$","$u^+$","$u^s$"]
    acc = np.zeros(shape=(4,3))
    time = np.zeros(shape = (4,3))
    acc_std = np.zeros(shape=(4,3))
    time_std = np.zeros(shape = (4,3))
    run = 50
    for i in range(len(fill_ratios)):
        for j in range(len(methods)):
            run_ =  f"/fill_ratio/parallel_{run}"
            x = get_folder_results(run_,batch_size)
            time_,acc_,tstd,astd = x.get_dec_time_acc(True)
            if fill_ratios[i] >.5:
                acc_= 1-acc_
            acc[i,j] = acc_
            time[i,j] = time_
            acc_std[i,j] = astd / np.sqrt(batch_size)
            time_std[i,j] = tstd / np.sqrt(batch_size)
            run+=1
    scaling = 0.5
    print(acc,time)
    plt.figure(figsize = (6.4 * scaling , 4.8 * scaling))
    for i in range(len(methods)):
        plt.plot(range(4),acc[:,i],label = str((methods[i])),color = c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
        plt.fill_between(range(4),acc[:,i]- acc_std[:,i],acc[:,i]+ acc_std[:,i] ,color = c_1[i], alpha=.3)
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    
    plt.yticks([0.70,0.75,0.80,0.85,0.90,0.95])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.25), ncol=4,fontsize= 10)
    plt.xlabel("Fill-ratio $(f)$")
    plt.ylabel("Accuracy")
    plt.tight_layout(pad = 0.05)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/result_fill_ratio_acc.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
        

    plt.figure(figsize = (6.4 * scaling , 4.8 * scaling))
    for i in range(len(methods)):
        plt.plot(range(4),time[:,i],label = str((methods[i])),color =c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
        plt.fill_between(range(4),time[:,i]- time_std[:,i],time[:,i]+ time_std[:,i] ,color = c_1[i], alpha=.3)
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.25), ncol=4,fontsize= 10)
    plt.xlabel("Fill-ratio $(f)$")
    plt.ylabel("Time")
    plt.tight_layout(pad = 0.05)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/result_fill_ratio_time.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
    plt.show()





    return

def plot_multi_robot():

    n_robots = [10,9,8,7,6,5]
    methods = ["$u^-$","$u^+$","$u^s$"]
    run = 100
    acc = np.zeros(shape=(3,6))
    CA_time = np.zeros(shape=(3,6))
    DD_time = np.zeros(shape=(3,6))
    CA_time_std = np.zeros(shape=(3,6))
    DD_std = np.zeros(shape=(3,6))
    time = np.zeros(shape = (3,6))
    acc_std = np.zeros(shape=(3,6))
    time_std = np.zeros(shape = (3,6))
    for n_r in range(len(n_robots)):
        for feedback in range(len(methods)):
            run_ = f"/multi_robot/parallel_{run}"
            x = get_folder_results(run_,batch_size)
            time_,acc_,time_std_,acc_std_ = x.get_dec_time_acc(True)
            _,_,ca_time_,_ = x.get_state_times()
            d,_,_,_,_ = x.compute_distances_and_directions()
            ca_time_ = create_one_array(ca_time_) / 1000
            CA_time[feedback,n_r] = np.mean(ca_time_)
            DD_time[feedback,n_r] =d.mean()
            DD_std[feedback,n_r] = d.std() / np.sqrt(batch_size)
            CA_time_std[feedback,n_r] = np.std(ca_time_) / np.sqrt(batch_size)
            acc[feedback,n_r] = acc_
            time[feedback,n_r] = time_
            acc_std[feedback,n_r] = acc_std_ / np.sqrt(batch_size)
            time_std[feedback,n_r] = time_std_/ np.sqrt(batch_size)
            run+=1

    scaling = 0.5
    plt.figure(figsize = (6.4 * scaling , 4.8 * scaling))
    for i in range(len(methods)):
        temp_ = np.flip(acc[i,:],axis=0)
        temp_std = np.flip(acc_std[i,:],axis=0)
        plt.plot(range(6),temp_,label = str((methods[i])),color = c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
        plt.fill_between(range(6), temp_ - temp_std, temp_ + temp_std,color = c_1[i],alpha = 0.3)

    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.25), ncol=4,fontsize= 9)
    plt.xlabel("Number of robots")
    plt.ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_acc.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)

    plt.figure(figsize = (6.4 * scaling, 4.8 * scaling))
    for i in range(len(methods)):
        temp_ = np.flip(CA_time[i,:],axis=0)
        temp_std = np.flip(CA_time_std[i,:],axis=0)
        plt.plot(range(6),temp_,label = str((methods[i])),color = c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
        plt.fill_between(range(6), temp_ - temp_std, temp_ + temp_std,color = c_1[i],alpha = 0.3)

    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.25), ncol=4,fontsize= 9)
    plt.xlabel("Number of robots")
    plt.ylabel("CA time [s]")
    plt.tight_layout()
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_ca_time.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)

    plt.figure(figsize = (6.4 * scaling , 4.8 * scaling))
    for i in range(len(methods)):
        temp_ = np.flip(DD_time[i,:],axis=0)
        temp_std = np.flip(DD_std[i,:],axis=0)
        plt.plot(range(6),temp_,label = str((methods[i])),color = c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
        plt.fill_between(range(6), temp_ - temp_std, temp_ + temp_std,color = c_1[i],alpha = 0.3)
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.25), ncol=4,fontsize= 9)
    plt.xlabel("Number of robots")
    plt.ylabel("Distance [m]")
    plt.tight_layout()
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_dist_driven.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)



    plt.figure(figsize = (6.4 * scaling , 4.8 * scaling))
    for i in range(len(methods)):
        temp_ = np.flip(time[i,:],axis=0)
        temp_std = np.flip(time_std[i,:],axis=0)
        plt.plot(range(6),temp_,label = str((methods[i])),color = c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
        plt.fill_between(range(6), temp_ - temp_std, temp_ + temp_std,color = c_1[i],alpha = 0.3)

    plt.yticks([400,500,600,700,800,900])
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.25), ncol=4,fontsize= 9)
    plt.xlabel("Number of robots")
    plt.ylabel("Time [s]")
    plt.tight_layout()
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_time.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
    plt.show()

    return





def plot_robustness_analysis():
    M1 = diagonal_matrix()
    M2 = stripe_matrix()
    M3 = block_diagonal_matrix()
    M4 = organized_alternating_matrix()
    M5 = random_matrix()
    M1_46 = diagonal_matrix_46()
    M2_46 = stripe_matrix_46()
    M3_46 = block_diagonal_matrix_46()
    M4_46 = organized_alternating_matrix_46()
    M5_46 = random_matrix(0.46)
    Ms = [M1,M2,M3,M4,M5,M1_46,M2_46,M3_46,M4_46,M5_46]
    matrices = ["$M_{1_{48}}$","$M_{2_{48}}$","$M_{3_{48}}$","$M_{4_{48}}$","$M_{5_{48}}$","$M_{1_{46}}$","$M_{2_{46}}$","$M_{3_{46}}$","$M_{4_{46}}$","$M_{5_{46}}$"]
    methods = ["$u^-$","$u^+$","$u^s$"]
    run = 150
    acc = np.empty(shape=(10,2,3),dtype=object)
    time = np.empty(shape = (10,2,3),dtype=object)
    acc_std = np.empty(shape=(10,2,3),dtype=object)
    time_std = np.empty(shape = (10,2,3),dtype=object)
    entropies = []
    MIs = []

    particles = [0,1]
    for m in range(len(matrices)):
        for part in particles:
            entropies.append(entropy(Ms[m]))
            MIs.append(calculate_morans_I(Ms[m]))
            for feedback in range(len(methods)):
                    run_ = f"/grid/parallel_{run}"
                    x = get_folder_results(run_,batch_size,size =10)
                    time_,acc_,time_std_,acc_std_ = x.get_dec_time_acc(True)
                    acc[m,part,feedback] = acc_
                    time[m,part,feedback] = time_
                    acc_std[m,part,feedback] = acc_std_
                    time_std[m,part,feedback] = time_std_
                    run+=1


    fig, axes = plt.subplots(5, 5,figsize = (6.4 * 1, 4.8 * 0.75*2), sharey='row')
    matrices_ = [M1, M2, M3, M4, M5]
    titles = ["Diagonal", "Stripe", "Block Diagonal", "Alternating", "Random"]

    for i, (matrix, title) in enumerate(zip(matrices_, titles)):
        ax = axes[0,i]
        ax.imshow(matrix, cmap="gray")
        ax.set_title(title,fontsize =7)
        ax.axis("on")
        ax.set_xticks([])
        ax.set_yticks([])
            # Show spines (borders) around each subplot
        for spine in ax.spines.values():
            spine.set_visible(True)       # Show each spine (border)
            spine.set_linewidth(1)        # Set the border width
            spine.set_color("black")      # Set the border color to black
    
    for j in range(5):
        ax_48_time = axes[1,j]
        ax_48_acc = axes[2,j]
        ax_46_time = axes[3,j]
        ax_46_acc = axes[4,j]

        for part in particles:
            time_48 = []
            acc_48 = []
            time_46 = []
            acc_46 = []
            for f in range(len(methods)):
                time_48.append(time[j,part,f])
                time_46.append(time[j+5,part,f])
                acc_48.append(acc[j,part,f])
                acc_46.append(acc[j+5,part,f])

            ax_48_time.plot(time_48)
            ax_48_acc.plot(acc_48)
            ax_46_time.plot(time_46)
            ax_46_acc.plot(acc_46)
            
                        
                        




        
    axes[0, 0].set_ylabel('Environment', fontsize=8)
    axes[1, 0].set_ylabel('Time [s]', fontsize=8)
    axes[2, 0].set_ylabel('Accuracy', fontsize=8)

    plt.subplots_adjust(left=0.0, right=1, top=1, bottom=0.0, wspace=0.01, hspace=0.01)

    
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/grid_analysis.pdf', format='pdf', bbox_inches='tight')#, pad_inches=0.025)
    
    plt.show()
    

        




if __name__ == "__main__":

    batch_size = 2
    plot_robustness_analysis()
