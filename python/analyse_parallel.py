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
            run_ = f"/Calibration_Us/parallel_{k}"
            x = get_folder_results(run_,batch_size)

            time,acc = x.get_dec_time_acc()
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            k+=1
    plt.figure()
    for i in range(len(usps)):
        plt.plot(etas,resulting_acc[:,i],label =f"$\kappa_{str(round(usps[i]/1000))}$",color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.axhline(0.72,label = "$u^-$",color = 'red',linestyle = '--')
    plt.xlabel("$\\eta$")
    plt.ylabel("Accuracy")
    plt.legend(loc='upper center', bbox_to_anchor=(0.425,1.25), ncol=5)
    plt.tight_layout(pad = 0.05)
    plt.savefig(f"/home/thiemenrug/Documents/OutputDir/JournalSI/figures/CalibrationUs_Accuracy.pdf")

    plt.figure()
    for i in range(len(usps)):
        plt.plot(etas,resulting_time[:,i],label =f"$\kappa_{str(round(usps[i]/1000))}$",color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.axhline(893,label = "$u^-$",color = 'red',linestyle = '--')
    plt.xlabel("$\\eta$")
    plt.ylabel("Time $[s]$")
    plt.legend(loc='upper center', bbox_to_anchor=(0.425,1.25), ncol=5)
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
    resulting_acc = np.zeros(shape=(4,3))
    resulting_time = np.zeros(shape = (4,3))
    run = 50
    for i in range(len(fill_ratios)):
        for j in range(len(methods)):
            run_ =  f"/fill_ratio/parallel_{run}"
            x = get_folder_results(run_,batch_size)
            time,acc = x.get_dec_time_acc()
            if fill_ratios[i] >.5:
                acc= 1-acc
            resulting_acc[i,j] = acc
            resulting_time[i,j] = time
            run+=1
    print(resulting_time,"\n",resulting_acc)
    time = resulting_time

    acc = resulting_acc

    plt.figure()
    for i in range(len(methods)):
        plt.plot(range(4),acc[:,i],label = str((methods[i])),color = c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.25), ncol=4,fontsize= 10)
    plt.xlabel("$f$")
    plt.ylabel("Accuracy")
    plt.tight_layout(pad = 0.05)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/result_fill_ratio_acc.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
    plt.figure()
    for i in range(len(methods)):
        plt.plot(range(4),time[:,i],label = str((methods[i])),color =c_1[i], linestyle = linestyles_[i],marker = markers_[i+2])
    plt.xticks(ticks=np.arange(len(fill_ratios)), labels=[str((u)) for u in (fill_ratios)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.25), ncol=4,fontsize= 10)
    plt.xlabel("$f$")
    plt.ylabel("Time")
    plt.tight_layout(pad = 0.05)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/result_fill_ratio_time.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
    plt.show()





    return

def plot_multi_robot():
    fill_ratios = [.48,.52]
    n_robots = [10,9,8,7,6,5]
    methods = ["$u^-$","$u^+$","$u^s$"]
    run = 100
    resulting_acc = np.zeros(shape=(2,6,3))
    col_time_p_sample = np.zeros(shape=(2,6,3))
    resulting_time = np.zeros(shape = (2,6,3))

    resulting_acc_std = np.zeros(shape=(2,6,3))
    resulting_time_std = np.zeros(shape = (2,6,3))
    for fill in range(len(fill_ratios)):
        for n_r in range(len(n_robots)):
            for feedback in range(len(methods)):
                run_ = f"/multi_robot/parallel_{run}"
                x = get_folder_results(run_,batch_size)
                time,acc,time_std,acc_std = x.get_dec_time_acc(True)
                _,_,ca_time,_ = x.get_state_times()
                ca_time = create_one_array(ca_time) / 1000
                col_time_p_sample[fill,n_r,feedback] = np.mean(ca_time)
                if fill >.5:
                    acc= 1-acc
                resulting_acc[fill,n_r,feedback] = acc
                resulting_time[fill,n_r,feedback] = time
                resulting_acc_std[fill,n_r,feedback] = acc_std
                resulting_time_std[fill,n_r,feedback] = time_std
                run+=1
    
    #select 0 or 1st index for 48 and 52 percent respectively
    time = resulting_time[0,:,:].transpose()
    col_time_p_sample = col_time_p_sample[0,:,:].transpose()
    print(col_time_p_sample)
    acc = resulting_acc[0,:,:].transpose()
    time_std = resulting_time_std[0,:,:].transpose()  
    acc_std = resulting_acc_std[0,:,:].transpose()    
    
    scaling = 0.5
    plt.figure(figsize = (6.4 * scaling*0.8 , 4.8 * scaling))
    for i in range(len(methods)):
        plt.plot(range(6),np.flip(acc[i,:],axis=0),label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
       # Secondary y-axis for CA (axis1)
    
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.4,1.25), ncol=4,fontsize= 10)
    plt.xlabel("$N_r$")
    plt.ylabel("Accuracy")
    plt.tight_layout(pad = 0.0)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_acc.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)

     
    plt.figure(figsize = (6.4 * scaling*0.8, 4.8 * scaling))
    for i in range(len(methods)):
        plt.plot(range(6),np.flip(col_time_p_sample[i,:],axis=0),label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
       
    
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.4,1.25), ncol=4,fontsize= 10)
    plt.xlabel("$N_r$")
    plt.ylabel("CA time [s]")
    plt.tight_layout(pad = 0.0)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_ca_time.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)

    plt.figure(figsize = (6.4 * scaling*0.8 , 4.8 * scaling))
    for i in range(len(methods)):
        plt.plot(range(6),np.flip(time[i,:],axis=0),label = str((methods[i])),color = "black", linestyle = linestyles_[i],marker = markers_[i+2])
    plt.yticks([200,300,400,500,600,700,800])
    plt.xticks(ticks=np.arange(len(n_robots)), labels=[str(round(u)) for u in reversed(n_robots)])
    plt.legend(loc='upper center', bbox_to_anchor=(0.4,1.25), ncol=4,fontsize= 10)
    plt.xlabel("$N_r$")
    plt.ylabel("Time [s]")
    
    plt.tight_layout(pad = 0.0)
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/multi_robot_time.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
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
    resulting_acc = np.empty(shape=(5,3),dtype=object)
    resulting_time = np.empty(shape = (5,3),dtype=object)

    objects = np.zeros(shape = (5,3))
    entropies = []
    MIs = []
    for m in range(len(matrices)):
        entropies.append(entropy(Ms[m]))
        MIs.append(calculate_morans_I(Ms[m]))
        for feedback in range(len(methods)):
                run_ = f"/grid_results/parallel_{run}"
                x = get_folder_results(run_,batch_size,size =10)
                time,acc = x.get_dec_time_acc_robots()
                resulting_acc[m,feedback] = acc
                resulting_time[m,feedback] = time
                run+=1
    # print(resulting_acc,"\n",resulting_time)
    # temp_acc = np.zeros(shape=(3,5,3))
    # temp_time = np.zeros(shape=(3,5,3))
    # for s in range(len(methods)):
    #     acc = resulting_acc[:,s]
    #     time = resulting_time[:,s]
    #     for m in range(len(matrices)):
    #         temp_acc[s,m,0] = acc[m]
    #         temp_acc[s,m,1] = entropies[m]
    #         temp_acc[s,m,2] = MIs[m]
    #         temp_time[s,m,0] = time[m]
    #         temp_time[s,m,1] = entropies[m]
    #         temp_time[s,m,2] = MIs[m]

    fig, axes = plt.subplots(3, 5,figsize = (6.4 * 1, 4.8 * 0.75), sharey='row')
    matrices = [M1, M2, M3, M4, M5]
    titles = ["Diagonal", "Stripe", "Block Diagonal", "Alternating", "Random"]

    for i, (matrix, title) in enumerate(zip(matrices, titles)):
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
    for i in range(1,3):
        for j in range(5):
            data = []
            for f in range(len(methods)):
                if i ==1:
                    temp_ = resulting_time[j,f]
                else:
                    temp_ = resulting_acc[j,f]
                data.append(temp_)
            ax = axes[i,j]
            ax.set_xticks(ticks=np.arange(len(methods)), labels=[str((u)) for u in (methods)])
            mean_values = np.mean(data, axis=1)
            std_values = np.std(data, axis=1)
            ax.plot(mean_values,linestyle = 'solid',marker = '*',linewidth =1.5,color= 'black')
            ax.errorbar(range(len(mean_values)), mean_values, yerr=std_values,
                linestyle='solid', marker='*', linewidth=1, color='black', capsize=3)
            ax.axis("on")
        
    axes[0, 0].set_ylabel('Environment', fontsize=8)
    axes[1, 0].set_ylabel('Time [s]', fontsize=8)
    axes[2, 0].set_ylabel('Accuracy', fontsize=8)

    plt.subplots_adjust(left=0.0, right=1, top=1, bottom=0.0, wspace=0.01, hspace=0.01)

    
    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/grid_analysis.pdf', format='pdf', bbox_inches='tight', pad_inches=0.025)
    
    plt.show()
    

        




if __name__ == "__main__":

    batch_size = 3
    plot_fill_ratio_result()
