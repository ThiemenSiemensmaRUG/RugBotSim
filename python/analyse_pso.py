import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random,time
import ast
# Update matplotlib rc parameters for Springer Nature single-column format
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",  # Use a serif font
    "font.size": 10,  # Font size typically 10pt for Springer Nature papers
    "axes.labelsize": 10,  # Label font size
    "axes.titlesize": 10,  # Title font size
    "legend.fontsize": 9,  # Legend font size
    "xtick.labelsize": 11,  # X-axis tick font size
    "ytick.labelsize": 11,  # Y-axis tick font size
    "lines.linewidth": 1.0,  # Line width
    "lines.markersize": 4,  # Marker size (adjusted for better visibility)
    "figure.figsize": (3.85, 2.75),  # Figure size in inches for a single column
    "figure.subplot.left": 0.1,  # Adjust subplot parameters as needed
    "figure.subplot.right": 0.95,
    "figure.subplot.bottom": 0.15,
    "figure.subplot.top": 0.85,
})
line_styles = [
    "-",      # Solid line
    "--",     # Dashed line
    "-.",     # Dash-dot line
    ":",      # Dotted line
    "solid",  # Solid line (equivalent to "-")
    "dashed", # Dashed line (equivalent to "--")
    "dashdot",# Dash-dot line (equivalent to "-.")
    "dotted", # Dotted line (equivalent to ":")
]


colors = []
random.seed(time.time())
for i in range(10):
    colors.append('#%06X' % random.randint(0, 0xFFFFFF))

line_markers = [
    ".",    # Point marker
    ",",    # Pixel marker
    "o",    # Circle marker
    "v",    # Triangle down marker
    "^",    # Triangle up marker
    "<",    # Triangle left markercolumn_names
    ">",    # Triangle right marker
    "1",    # Tri down marker
    "2",    # Tri up marker
    "3",    # Tri left marker
    "4",    # Tri right marker
    "s",    # Square marker
    "p",    # Pentagon marker
    "*",    # Star marker
    "h",    # Hexagon1 marker
    "H",    # Hexagon2 marker
    "+",    # Plus marker
    "x",    # X marker
    "D",    # Diamond marker
    "d",    # Thin diamond marker
]


def convert_to_list(string):
    return ast.literal_eval(string)

def calculate_mean(lst):
    return np.mean(lst)

def create_ones_array(array):
    array_length = len(array)
    return np.ones(array_length)

def normalize_vector(vector, max_val, min_val):
    # Ensure max_val and min_val are numpy arrays
    max_val = np.array(max_val)
    min_val = np.array(min_val)
    
    # Perform normalization
    normalized_vector = (np.array(vector) - min_val) / (max_val - min_val)
    
    return normalized_vector


def calculate_distance_vector(vector1, vector2):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    return np.linalg.norm(vector1 - vector2)


def plot_short_results(file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file ,header=None, names=["Iteration", "Global_Best", "m_p_b","g_b_pos"])
    df = df[:-1]
    df["g_b_pos"]  = df.iloc[:, -1].apply(lambda x: np.fromstring(x.strip('[]'), sep=' ')).values
    df["true"] = df["g_b_pos"].apply(create_ones_array)
    df['distance'] = df.apply(lambda row: calculate_distance_vector(row.iloc[3], row.iloc[4]), axis=1)
    # Extract the x and y values for the plot
    iterations = df['Iteration']
    global_best = df['Global_Best']
    distance = df['distance']

    return iterations,global_best,distance

class analyse():
    def __init__(self,filename = "pso_output/test.csv") -> None:
        self.filename = filename
        self.df = pd.read_csv(self.filename)
        self.df['Fitness_vals'] = self.df['Fitness_vals'].apply(convert_to_list)
        self.df['Fitness'] =self.df['Fitness_vals'].apply(calculate_mean)
        

        self.min_iter = min(self.df['Iteration'])
        self.max_iter = max(self.df['Iteration'])+1
        self.n_particles = max(self.df['Particle'])

        pass

    def get_results(self):
        mean_fitness = np.zeros(self.max_iter)
        global_best = np.ones(self.max_iter) * np.inf
        std_fitness = np.zeros(self.max_iter)
        fitness_vals = np.zeros(shape=(self.max_iter,self.n_particles))
        personal_best = np.ones(shape = (self.max_iter,self.n_particles))*10000000000
        mean_personal_best = np.ones(self.max_iter)*np.inf
        for i in range(self.min_iter,self.max_iter):
            df1 = self.df[self.df['Iteration']==i]
            fitness_vals[i,:] = df1['Fitness'].astype(float)
            mean_fitness[i] = df1['Fitness'].astype(float).mean()
            std_fitness[i] = df1['Fitness'].astype(float).std()
            min_iteration = df1['Fitness'].astype(float).min()
            if all(min_iteration < i for i in global_best):
                global_best[i] = min_iteration
            else:
                global_best[i] = global_best[i-1]
            for p in range(0,self.n_particles):
                df_p_i = df1[(df1['Particle'] -1) == p]
                
                min_iteration_p = df_p_i['Fitness'].astype(float).min()
                if all(min_iteration_p < j for j in personal_best[:,p]):
                    personal_best[i,p] = min_iteration_p
                else:
                    personal_best[i,p] = personal_best[i-1,p]
        mean_personal_best = personal_best.mean(axis = 1)
        std_personal_best = personal_best.std(axis = 1)        
        iterations = self.df['Iteration']

        return iterations,fitness_vals,mean_personal_best,std_personal_best,global_best



    def get_dimensions(self,bounds=None):
        # Strip leading and trailing whitespace from the 'position' column
        self.df['position'] = self.df['position'].str.strip().str.replace(r'^\[|\]$', '', regex=True)
        self.df['position'] = self.df['position'].str.strip()
        # Split the values in 'position' by one or more spaces and expand them into separate columns
        df_expanded = self.df['position'].str.split(r'\s+', expand=True)

        # Dynamically rename the new columns based on the number of split columns
        df_expanded.columns = [f'x{i+1}' for i in range(df_expanded.shape[1])]

        self.df_final = pd.concat([self.df, df_expanded], axis=1)

        dimensions = np.ones(shape = (self.max_iter,df_expanded.shape[1]))
        std = np.ones(shape = (self.max_iter,df_expanded.shape[1]))
        for i in range(self.min_iter,self.max_iter):
            
            df1 = self.df_final[self.df['Iteration']==i]
            for j in range(df_expanded.shape[1]):
                if bounds.all() != None:
              
                    print(df1['x' + str(j+1)].astype(float).mean())
                    d = normalize_vector(df1['x' + str(j+1)].astype(float),bounds[j][1],bounds[j][0])
                    print(d.mean())
                else:
                    d = df1['x' + str(j+1)].astype(float)
                dimensions[i,j] = d.mean()
                std[i,j] = d.std()

        return  dimensions,std

## processing the long output file
x=analyse("jobfiles/pso_7.csv")
iterations,fitness_vals,mean_personal_best,std_personal_best,global_best=x.get_results()
plt.figure()
plt.plot(range(0,x.max_iter),mean_personal_best,label="$\\mu (\mathcal{P}_i)$")

plt.plot(range(x.max_iter),np.mean(fitness_vals,axis=1),color = 'red',linestyle = line_styles[1],label="$\\mu (\mathcal{C}_i)$",marker = line_markers[3])



plt.fill_between(range(0,x.max_iter),mean_personal_best - std_personal_best, mean_personal_best + std_personal_best,label = "$\\sigma (\mathcal{P}_i)$",alpha = .4)
plt.plot(range(0,x.max_iter),global_best,label = '$\mathcal{G}_b$',linestyle = line_styles[2],marker = line_markers[0])
plt.xlabel("Iterations")
plt.ylabel("Fitness Value")
plt.grid()
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=4)
plt.tight_layout()
#plt.savefig('convergence.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)

bounds = np.array([[0,20000],[0,20000],[1000,6000],[50,150],[0,500]])

columns = ["$\\gamma_0$","$\gamma$","$\\tau$","$\\theta_C$","$O_c$"]
means,stds = x.get_dimensions(bounds=bounds)




plt.figure()
for i in range(5):
    plt.plot(range(0,means.shape[0]),means[:,i],marker = line_markers[i],linestyle = line_styles[i],label = columns[i],color = colors[i])
    plt.fill_between(range(0,means.shape[0]),means[:,i] - stds[:,i] ,means[:,i] + stds[:,i],color = colors[i],alpha=.2)

plt.xlabel("Iterations")
plt.ylabel("$\mu (\mathbf{p}_i)$")
plt.grid()
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=5)
plt.tight_layout()
#plt.savefig('dimensions.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)
plt.show()