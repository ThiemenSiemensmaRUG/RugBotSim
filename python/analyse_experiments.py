from webots_log_processor import WebotsProcessor,preprocess_multi_exp
import numpy as np
import matplotlib.pyplot as plt
from utils import *
import seaborn as sns

plt.rcParams.update({
    "axes.labelsize": 10,  # Label font size
    "axes.titlesize": 10,  # Title font size
    "legend.fontsize": 7.5,  # Legend font size
    "xtick.labelsize": 10,  # X-axis tick font size
    "ytick.labelsize": 10,  # Y-axis tick font size
    "lines.linewidth": 1.0,  # Line width
    "lines.markersize": 3,  # Marker size (adjusted for better visibility)
})
plt.rcParams['axes.prop_cycle'] = plt.cycler('color', ['black', 'black', 'black', 'blue', 'orange', 'purple'])


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


folder = "/home/thiemenrug/Documents/mrr/"

n_rovs = np.array([5,6,7,8,9,10])


# for rov in n_rovs:
#     _f = folder + f"{rov}_rovs/"
#     for i in range(1,17):
#         try:
#             file = f"/{rov}_rov_exp_{i}.csv"
#             _ = pd.read_csv(_f + file)
#             preprocess_multi_exp(_f,file,_f,f"_{i}")
#             print(rov,i)
#         except:
#             None
    


#files used

_5 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
_6 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
_7 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
_8 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
_9 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
_10 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
datasets = [_5,_6,_7,_8,_9,_10]

times_umin = np.empty(6, dtype=object)
accuracies_umin = np.empty(6, dtype=object)

times_uplus = np.empty(6, dtype=object)
accuracies_uplus = np.empty(6, dtype=object)

times_us = np.empty(6, dtype=object)
accuracies_us = np.empty(6, dtype=object)


for i,rov in enumerate(n_rovs):

    Umin_f = [f"{rov}_rovs/Umin_{i}.csv" for i in datasets[rov-5]]
    Uplus_f = [f"{rov}_rovs/Uplus_{i}.csv" for i in datasets[rov-5]]
    Us_f = [f"{rov}_rovs/Us_{i}.csv" for i in datasets[rov-5]]
    x_min = get_batch_results(folder,Umin_f)
    x_plus = get_batch_results(folder,Uplus_f)
    x_s = get_batch_results(folder,Us_f)
    
    t,a = x_min.get_dec_time_acc_robots()
    times_umin[i] = t
    accuracies_umin = a

    t,a = x_plus.get_dec_time_acc_robots()
    times_uplus[i] = t
    accuracies_uplus = a

    t,a = x_s.get_dec_time_acc_robots()
    times_us[i] = t
    accuracies_us[i] = a




# Assuming `times_umin` is filled with lists or arrays of times for each number of robots
n_rovs = [5, 6, 7, 8, 9, 10]  # Number of robots corresponding to `times_umin`

# Convert `times_umin` to a structure suitable for plotting
# Flatten and prepare data for violin plot
times_umin = [np.array(times_umin[i]).flatten() for i in range(len(times_umin))]
times_uplus = [np.array(times_uplus[i]).flatten() for i in range(len(times_uplus))]
times_us = [np.array(times_us[i]).flatten() for i in range(len(times_us))]

# Combine all datasets into one for plotting
all_times = [times_umin, times_uplus, times_us]
colors = ["black", "red", "green"]
labels = ["$u^-$", "$u^+$", "$u^s$"]

# Calculate mean values for each dataset
means = [np.array([np.mean(times) for times in dataset]) for dataset in all_times]
standard_errors = [np.array([np.std(times) / np.sqrt(len(times)) for times in dataset]) for dataset in all_times]


# Plot settings
fig, ax = plt.subplots(figsize=(6.4, 4))

# Create grouped violin plots
for i, times in enumerate(all_times):
    # Offset each group slightly for separation
    positions = np.arange(1, len(n_rovs) + 1) + i * 0.25  # Reduced offset for tighter spacing
    parts = ax.violinplot(
        times, 
        positions=positions, 
        showmeans=False, 
        showmedians=False, 
        widths=0.2  # Reduce violin width to prevent overlap
    )

    # Customize the appearance for one-sided violins
    for idx, pc in enumerate(parts['bodies']):
        # Clip the violin to the right side
        path = pc.get_paths()[0]
        vertices = path.vertices
        vertices[:, 0] = np.clip(vertices[:, 0], np.mean(vertices[:, 0]), None)  # Keep right side
        pc.set_facecolor(colors[i])
        pc.set_edgecolor('black')
        pc.set_alpha(0.6)

        # Scatter points on the left side
        x_scatter = np.random.uniform(low=positions[idx] - 0.1, high=positions[idx] - 0.05, size=len(times[idx]))
        ax.scatter(x_scatter, times[idx], color=colors[i], alpha=0.7, s=7, label="_nolegend_")  # Avoid duplicate legend

    # Customize violin parts
    #parts['cmedians'].set_color('orange')  # Median color
    parts['cmins'].set_color('black')  # Min color
    parts['cmaxes'].set_color('black')  # Max color

# Plot the mean as line plots
for i, (mean, se) in enumerate(zip(means, standard_errors)):
    ax.plot(
        np.arange(1, len(n_rovs) + 1) + i * 0.25,  # Match violin x-positions
        mean,
        marker='o',
        color=colors[i],
        label=f"Mean {labels[i]}",
        linestyle='--',
        markersize=6,
        markeredgecolor = "black",
        linewidth=1.5
    )
    # Adding error bars (standard error)
    ax.errorbar(
        np.arange(1, len(n_rovs) + 1) + i * 0.25,  # Match violin x-positions
        mean,
        yerr=se,  # Standard error
        fmt='o',
        color=colors[i],
        markersize=6,
        markeredgecolor = "black",
        linestyle='',
        capsize=5,  # Error bar cap size
        elinewidth=2
    )

# Adjust x-axis for grouped appearance
ax.set_xticks(np.arange(1, len(n_rovs) + 1) + 0.2)  # Center x-ticks
ax.set_xticklabels(n_rovs)
ax.set_xlabel("Number of Robots")
ax.set_ylabel("Decision Times")

# Create a general legend above the figure
handles, labels_legend = ax.get_legend_handles_labels()
ax.legend(
    handles=handles, 
    labels=[f"{label}" for label in labels],  # Adjusted legend labels
    loc="upper center", 
    bbox_to_anchor=(0.5, 1.15),  # Place legend above the figure
    ncol=3,  # Place the legend in 3 columns
    fontsize=12
)

# Add grid for better readability
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Save as PDF
output_path = "violin_plot_with_mean_lines.pdf"
plt.tight_layout()
plt.savefig(output_path, format='pdf')  # Save the figure as a PDF
print(f"Plot saved as {output_path}")

# Show the plot
plt.show()









# folder = "/home/thiemenrug/Documents/OutputDir/JournalSI/data/Real/"
# figfolder = "/home/thiemenrug/Documents/OutputDir/JournalSI/figures/"
# simfolder = "/home/thiemenrug/Documents/OutputDir/JournalSI/data/Real/"
# Uminsim = [f"Umin_sim/webots_log_{i}.txt" for i in range(10)]
# Uplussim = [f"UPlus_sim/webots_log_{i}.txt" for i in range(10)]
# Ussim = [f"Us_sim/webots_log_{i}.txt" for i in range(10)]

# Uminsim = get_batch_results(simfolder,Uminsim)
# Uplussim = get_batch_results(simfolder,Uplussim)
# Ussim = get_batch_results(simfolder,Ussim)

# Uminfiles = [f"UMIN{i}.csv" for i in range(1,11)]
# Uplusfiles = [f"UPLUS{i}.csv" for i in range(1,11)]
# Usfiles = [f"US{i}.csv" for i in range(1,11)]

# Umin = get_batch_results(folder,Uminfiles)
# Uplus = get_batch_results(folder,Uplusfiles)
# Us = get_batch_results(folder,Usfiles)

# bplot_acc = []
# bplot_time = []

# scaling = 0.5

# plt.figure(figsize = (6.4 * scaling, 4.8 * scaling))
# plt.ylim([0.3,1])
# t,p = Umin.compute_average_belief_over_time()
# df_t, df_acc = Umin.get_dec_time_acc_robots()
# bplot_acc.append(df_acc)
# bplot_time.append(df_t)
# plt.plot(t,p,label ="$u^-$",linestyle=linestyles_[1],color = "black")

# t,p = Uplus.compute_average_belief_over_time()
# df_t, df_acc = Uplus.get_dec_time_acc_robots()
# bplot_acc.append(df_acc)
# bplot_time.append(df_t)
# plt.plot(t,p,label ="$u^+$",linestyle=linestyles_[2],color = "red")

# t,p = Us.compute_average_belief_over_time()
# df_t, df_acc = Us.get_dec_time_acc_robots()
# bplot_acc.append(df_acc)
# bplot_time.append(df_t)
# plt.plot(t,p,label ="$u^s$",linestyle=linestyles_[3],color ="green")

# plt.xlabel("Time [s]")
# plt.ylabel("Belief")
# plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.25), ncol=4,fontsize= 9)
# plt.tight_layout()

# plt.savefig(figfolder + "/exp_exp_belief.pdf")

# bplot_acc_sim = []
# bplot_time_sim = []

# plt.figure(figsize = (6.4 * scaling, 4.8 * scaling))
# plt.ylim([0.3,1])
# t,p = Uminsim.compute_average_belief_over_time()
# df_t, df_acc = Uminsim.get_dec_time_acc_robots()
# bplot_acc_sim.append(df_acc)
# bplot_time_sim.append(df_t)
# plt.plot(t,p,label ="$u^-$",linestyle=linestyles_[1],color = "black")

# t,p = Uplussim.compute_average_belief_over_time()
# df_t, df_acc = Uplussim.get_dec_time_acc_robots()
# bplot_acc_sim.append(df_acc)
# bplot_time_sim.append(df_t)
# plt.plot(t,p,label ="$u^+$",linestyle=linestyles_[2],color = "red")

# t,p = Ussim.compute_average_belief_over_time()
# df_t, df_acc = Ussim.get_dec_time_acc_robots()
# bplot_acc_sim.append(df_acc)
# bplot_time_sim.append(df_t)
# plt.plot(t,p,label ="$u^s$",linestyle=linestyles_[3],color ="green")

# plt.xlabel("Time [s]")
# plt.ylabel("Belief")
# plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.25), ncol=4,fontsize= 9)
# plt.tight_layout()
# plt.savefig(figfolder + "exp_sim_belief.pdf")


# plt.figure(figsize = (6.4 * scaling, 4.8 * scaling))
# plt.ylim([-0.1,1.1])
# plt.ylabel("Accuracy [s]")
# poss= [0.75, 1.25,  2.25,2.75, 3.75, 4.25]
# box = plt.boxplot([bplot_acc_sim[0],bplot_acc[0],bplot_acc_sim[1],bplot_acc[1],bplot_acc_sim[2],bplot_acc[2]],positions = poss, widths=0.4, patch_artist=True)
# colors_sim = 'mediumblue'
# colors_real = 'lightcoral'
# # Define colors for simulation and real
# for i, patch in enumerate(box['boxes']):
#     if i % 2 == 0:  # Sim data (even indices)
#         patch.set_facecolor(colors_sim)
#     else:  # Real data (odd indices)
#         patch.set_facecolor(colors_real)


# for i, (sim_data, real_data) in enumerate(zip(bplot_acc_sim, bplot_acc)):
#     x_sim = np.random.normal(poss[2*i], 0.05, size=len(sim_data))
#     x_real = np.random.normal(poss[2*i + 1], 0.05, size=len(real_data))
#     plt.scatter(x_sim, sim_data, color='black', alpha=0.5, label="Sim" if i == 0 else "", zorder=3,s=1)
#     plt.scatter(x_real, real_data, color='black', alpha=0.5, label="Real" if i == 0 else "", zorder=3,s=1)



# plt.xticks([1, 2.5, 4], ['$u^-$', '$u^+$', '$u^s$'])
# plt.legend([box["boxes"][0], box["boxes"][1]], ['Sim', 'Real'], loc='upper right', bbox_to_anchor=(0.85,1.2), ncol=2,fontsize = 9)
# plt.tight_layout()
# plt.savefig( figfolder  + "/bb_acc_exp.pdf")


# plt.figure(figsize = (6.4 * scaling, 4.8 * scaling))
# plt.ylim([400,1200])
# plt.ylabel("Time [s]")
# poss= [0.75, 1.25,  2.25,2.75, 3.75, 4.25]
# box = plt.boxplot([bplot_time_sim[0],bplot_time[0],bplot_time_sim[1],bplot_time[1],bplot_time_sim[2],bplot_time[2]],positions = poss, widths=0.4, patch_artist=True)
# colors_sim = 'mediumblue'
# colors_real = 'lightcoral'
# # Define colors for simulation and real
# for i, patch in enumerate(box['boxes']):
#     if i % 2 == 0:  # Sim data (even indices)
#         patch.set_facecolor(colors_sim)
#     else:  # Real data (odd indices)
#         patch.set_facecolor(colors_real)

# for i, (sim_data, real_data) in enumerate(zip(bplot_time_sim, bplot_time)):
#     x_sim = np.random.normal(poss[2*i], 0.05, size=len(sim_data))
#     x_real = np.random.normal(poss[2*i + 1], 0.05, size=len(real_data))
#     plt.scatter(x_sim, sim_data, color='black', alpha=0.5, label="Sim" if i == 0 else "", zorder=3,s=1)
#     plt.scatter(x_real, real_data, color='black', alpha=0.5, label="Real" if i == 0 else "", zorder=3,s=1)


# plt.xticks([1, 2.5, 4], ['$u^-$', '$u^+$', '$u^s$'])
# plt.legend([box["boxes"][0], box["boxes"][1]], ['Sim', 'Real'], loc='upper right', bbox_to_anchor=(0.85,1.2), ncol=2,fontsize = 9)
# plt.tight_layout()
# plt.savefig(figfolder + "/bb_time_exp.pdf")
# plt.show()
