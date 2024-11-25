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


CA_times = np.empty(6,dtype= object)

for i,rov in enumerate(n_rovs):

    Umin_f = [f"{rov}_rovs/Umin_{i}.csv" for i in datasets[rov-5]]
    Uplus_f = [f"{rov}_rovs/Uplus_{i}.csv" for i in datasets[rov-5]]
    Us_f = [f"{rov}_rovs/Us_{i}.csv" for i in datasets[rov-5]]
    x_min = get_batch_results(folder,Umin_f)
    x_plus = get_batch_results(folder,Uplus_f)
    x_s = get_batch_results(folder,Us_f)
    
    t,a = x_min.get_dec_time_acc_robots()
    times_umin[i] = t
    accuracies_umin[i] = a

    t,a = x_plus.get_dec_time_acc_robots()
    times_uplus[i] = t
    accuracies_uplus[i] = a

    t,a = x_s.get_dec_time_acc_robots()
    times_us[i] = t
    accuracies_us[i] = a

plot_dec_time = False

plot_dec_acc = True

accuracies_umin = [np.array(accuracies_umin[i]).flatten() for i in range(len(accuracies_umin))]
accuracies_uplus = [np.array(accuracies_uplus[i]).flatten() for i in range(len(accuracies_uplus))]
accuracies_us = [np.array(accuracies_us[i]).flatten() for i in range(len(accuracies_us))]
all_acc = [accuracies_umin,accuracies_uplus,accuracies_us]

mean_accs = [np.array([np.mean(acc) for acc in dataset]) for dataset in all_acc]
std_accs = [np.array([np.std(acc) / np.sqrt(len(acc))  for acc in dataset]) for dataset in all_acc]

# Assuming `times_umin` is filled with lists or arrays of times for each number of robots
n_rovs = [5, 6, 7, 8, 9, 10]  # Number of robots corresponding to `times_umin`

# Convert `times_umin` to a structure suitable for plotting
# Flatten and prepare data for violin plot
times_umin = [np.array(times_umin[i]).flatten() for i in range(len(times_umin))]
times_uplus = [np.array(times_uplus[i]).flatten() for i in range(len(times_uplus))]
times_us = [np.array(times_us[i]).flatten() for i in range(len(times_us))]

if plot_dec_time:
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




if plot_dec_acc:
    colors = ["black", "red", "green"]
    labels = ["$u^-$", "$u^+$", "$u^s$"]
    fig, ax = plt.subplots(figsize=(6.4*0.5, 4.8*0.5))
    # Plot the mean as line plots
    for i, (mean, se) in enumerate(zip(mean_accs, std_accs)):
        ax.plot(
            np.arange(1, len(n_rovs) + 1) + i * 0.2,  # Match violin x-positions
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
            np.arange(1, len(n_rovs) + 1) + i * 0.2,  # Match violin x-positions
            mean,
            yerr=se,  # Standard error
            fmt='o',
            color=colors[i],
            markersize=6,
            markeredgecolor = "black",
            linestyle='',
            capsize=3,  # Error bar cap size
            elinewidth=1
        )

    # Adjust x-axis for grouped appearance
    ax.set_xticks(np.arange(1, len(n_rovs) + 1) + 0.2)  # Center x-ticks
    ax.set_xticklabels(n_rovs)
    ax.set_xlabel("Number of Robots")
    ax.set_ylabel("Accuracy")

    # Create a general legend above the figure
    handles, labels_legend = ax.get_legend_handles_labels()
    ax.legend(
        handles=handles, 
        labels=[f"{label}" for label in labels],  # Adjusted legend labels
        loc="upper center", 
        bbox_to_anchor=(0.5, 1.15),  # Place legend above the figure
        ncol=3,  # Place the legend in 3 columns
        fontsize=10
    )
    plt.tight_layout()
    plt.show()