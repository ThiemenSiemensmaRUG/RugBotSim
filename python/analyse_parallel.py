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


def plot_grid_results_error_bars(axs, index, time_arr, acc_arr, time_arr_std, acc_arr_std):
    t = -0.1
    colors = ['red','green']
    for part in [0, 1]:
        if part == 0:
            label = "$P^*$"
        else:
            label = "$P_0$"
        # Define axes for each part
        ax_48_time = axs[1, index]
        ax_48_acc = axs[3, index]
        ax_46_time = axs[2, index]
        ax_46_acc = axs[4, index]

        # Extract data
        time_48 = time_arr[index, part, :]
        acc_48 = acc_arr[index, part, :]
        time_46 = time_arr[index + 5, part, :]
        acc_46 = acc_arr[index+5, part, :]

        # Extract standard deviations
        time_48_std = time_arr_std[index, part, :]  #/ np.sqrt(batch_size)
        acc_48_std = acc_arr_std[index + 5, part, :] #/ np.sqrt(batch_size)
        time_46_std = time_arr_std[index + 5, part, :] #/ np.sqrt(batch_size)
        acc_46_std = acc_arr_std[index, part, :]# / np.sqrt(batch_size)

        # X positions for the scatter plot
        x_vals = np.linspace(0, 2, 3) + t

        # Plot points with error bars
        ax_48_time.errorbar(x_vals, time_48, yerr=time_48_std, fmt='o', color=colors[part], label=label)
        ax_48_acc.errorbar(x_vals, acc_48, yerr=acc_48_std, fmt='o', color=colors[part], label=label)
        ax_46_time.errorbar(x_vals, time_46, yerr=time_46_std, fmt='o', color=colors[part], label=label)
        ax_46_acc.errorbar(x_vals, acc_46, yerr=acc_46_std, fmt='o', color=colors[part], label=label)

        t += 0.2  # Increment offset for the next part



def plot_grid_results_belief(axs, index, beliefs,beliefs_std,methods):
    ax_belief_48_Pstar = axs[1, index]
    ax_belief_48_P0 = axs[2, index]
    ax_belief_46_Pstar = axs[3, index]
    ax_belief_46_P0 = axs[4, index]
    cs = ['black','red','green']
    for i in range(len(methods)):
        belief_48 = beliefs[index,0,i]
        belief_48_ = beliefs[index,1,i]
        belief_46 = beliefs[index+5,0,i]
        belief_46_ = beliefs[index+5,1,i]

        belief_48_std = beliefs_std[index,0,i] / np.sqrt(batch_size)
        belief_48_std_ = beliefs_std[index,1,i] / np.sqrt(batch_size)
        belief_46_std = beliefs_std[index+5,0,i] / np.sqrt(batch_size)
        belief_46_std_ = beliefs_std[index+5,1,i] / np.sqrt(batch_size)

        ax_belief_48_Pstar.plot(belief_48,label = methods[i],color = cs[i])
        ax_belief_48_Pstar.fill_between(range(1201),belief_48 - belief_48_std, belief_48 + belief_48_std, color= cs[i],alpha=.3)

        ax_belief_48_P0.plot(belief_48_,label = methods[i],color = cs[i])
        ax_belief_48_P0.fill_between(range(1201),belief_48_ - belief_48_std_, belief_48_ + belief_48_std_, color= cs[i],alpha=.3)

        ax_belief_46_Pstar.plot(belief_46,label = methods[i],color = cs[i])
        ax_belief_46_Pstar.fill_between(range(1201),belief_46 - belief_46_std, belief_46 + belief_46_std, color= cs[i],alpha=.3)

        ax_belief_46_P0.plot(belief_46_,label = methods[i],color = cs[i])
        ax_belief_46_P0.fill_between(range(1201),belief_46_ - belief_46_std_, belief_46_ + belief_46_std_, color= cs[i],alpha=.3)

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
    for m in Ms:
        print(f"MI:{calculate_morans_I(m)}, E:{entropy(m)}")
    matrices = ["$M_{1_{48}}$","$M_{2_{48}}$","$M_{3_{48}}$","$M_{4_{48}}$","$M_{5_{48}}$","$M_{1_{46}}$","$M_{2_{46}}$","$M_{3_{46}}$","$M_{4_{46}}$","$M_{5_{46}}$"]
    methods = ["$u^-$","$u^+$","$u^s$"]
    run = 150
    acc = np.empty(shape=(10,2,3),dtype=object)
    time = np.empty(shape = (10,2,3),dtype=object)
    acc_std = np.empty(shape=(10,2,3),dtype=object)
    time_std = np.empty(shape = (10,2,3),dtype=object)
    beliefs = np.empty(shape = (10,2,3),dtype = object)
    beliefs_std = np.empty(shape = (10,2,3),dtype = object)
    entropies = []
    MIs = []
    #set output to "belief" to plot belief
    output = "d"
    particles = [0,1]
    for m in range(len(matrices)):
        for part in particles:
            entropies.append(entropy(Ms[m]))
            MIs.append(calculate_morans_I(Ms[m]))
            for feedback in range(len(methods)):
                    run_ = f"/grid/parallel_{run}"
                    x = get_folder_results(run_,batch_size,size =10)
                    time_,acc_,time_std_,acc_std_ = x.get_dec_time_acc(True)
                    _, beliefs[m,part,feedback] = x.compute_average_belief_over_time()
                    _, beliefs_std[m,part,feedback] = x.compute_std_beliefs_over_time()
                    acc[m,part,feedback] = acc_
                    time[m,part,feedback] = time_
                    acc_std[m,part,feedback] = acc_std_
                    time_std[m,part,feedback] = time_std_
                    run+=1

    print(time.astype(float))

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
        if output == "belief":
            plot_grid_results_belief(axes, j, beliefs,beliefs_std,methods)
        else:
            plot_grid_results_error_bars(axes,j,time,acc,time_std,acc_std)
        
        
    if output == "belief":
        for ax_row in axes[:-1]:  # Iterate through rows except the last row
            for ax in ax_row:
                ax.label_outer()  # Hides x-axis labels and ticks on all but the last row
        for ax in axes[-1]:  # Iterate through the last row
            ax.set_xlabel("Time [s]")
        for ax in axes[1:,0]:
            ax.set_ylim(0.45,0.95)
        axes[1,0].set_ylabel("$p(P^*)|_{f=0.48}$",fontsize = 7)
        axes[2,0].set_ylabel("$p(P_0)|_{f=0.48}$",fontsize = 7)
        axes[3,0].set_ylabel("$p(P^*)|_{f=0.46}$",fontsize = 7)
        axes[4,0].set_ylabel("$p(P_0)|_{f=0.46}$",fontsize = 7)
        axes[1,2].legend(loc='upper center',ncols=3,bbox_to_anchor=(0.5,1.25),fontsize=6)


    else:
        axes[1,0].set_ylim(0,1300)
        axes[2,0].set_ylim(0,1300)
        axes[3,0].set_ylim(0.5,1)
        axes[4,0].set_ylim(0.5,1)
        for ax in axes[1:4, :].flatten():  # Flatten in case it's a 2D array of axes
            ax.set_xticks(range(3))
            ax.set_xticklabels([])
            ax.grid()
        for ax in axes[4:, :].flatten():  # Flatten in case it's a 2D array of axes
            ax.set_xticks(range(3))
            ax.set_xticklabels(methods,fontsize=8)
            ax.grid()
        for ax in axes[1,:]:
            ax.legend(loc='upper center',ncols=2,bbox_to_anchor=(0.5,1.25),fontsize=6)
        for ax in axes[3:,0]:
            ax.set_yticks([0.5,0.75,1.0])
        axes[0, 0].set_ylabel('Environment', fontsize=8)
        axes[1, 0].set_ylabel('$\\text{Time}_{f=0.48}$', fontsize=8)
        axes[2, 0].set_ylabel('$\\text{Time}_{f=0.46}$', fontsize=8)
        axes[3, 0].set_ylabel('$\\text{Accuracy}_{f=0.48}$', fontsize=8)
        axes[4, 0].set_ylabel('$\\text{Accuracy}_{f=0.46}$', fontsize=8)

    plt.subplots_adjust(left=0.0, right=1, top=1, bottom=0.0, wspace=0.01, hspace=0.01)

    plt.savefig('/home/thiemenrug/Documents/OutputDir/JournalSI/figures/grid_analysis.pdf', format='pdf', bbox_inches='tight')#, pad_inches=0.025)
    
    plt.show()
    
def plot_robustness_analysis_2():
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
    beliefs = np.empty(shape = (10,2,3),dtype = object)
    beliefs_std = np.empty(shape = (10,2,3),dtype = object)
    entropies = []
    MIs = []
    #set output to "belief" to plot belief
    output = "belief"
    particles = [0,1]
    for m in range(len(matrices)):
        for part in particles:
            entropies.append(entropy(Ms[m]))
            MIs.append(calculate_morans_I(Ms[m]))
            for feedback in range(len(methods)):
                    run_ = f"/grid/parallel_{run}"
                    x = get_folder_results(run_,batch_size,size =10)
                    time_,acc_,time_std_,acc_std_ = x.get_dec_time_acc(True)
                    _, beliefs[m,part,feedback] = x.compute_average_belief_over_time()
                    _, beliefs_std[m,part,feedback] = x.compute_std_beliefs_over_time()
                    acc[m,part,feedback] = acc_
                    time[m,part,feedback] = time_
                    acc_std[m,part,feedback] = acc_std_
                    time_std[m,part,feedback] = time_std_
                    run+=1

    print(time.astype(float))

        




if __name__ == "__main__":

    batch_size = 100

    plot_robustness_analysis()
