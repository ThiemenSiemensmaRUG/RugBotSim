import numpy as np
from webots import WebotsEvaluation
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent.futures
from utils import *
import os
import shutil

def remove_dir(directory):
    # Method to delete the run directory    
    if os.path.exists(directory):
        shutil.rmtree(directory)
        
    else:
        raise FileNotFoundError(f"Source directory not found at {directory}")





def launch_instance(x,reevaluation = 0,run_dir=0,feedback =0,fill_ratio = 0.48,n_robots= 5,grid = None,gridsize = 5,desc = "None"):
    instance = reevaluation
    if fill_ratio > .5:
        right_dec=1
    else:
        right_dec = 0
    job = WebotsEvaluation(run = run_dir,instance = reevaluation,robots=n_robots)
    
    world_creation_seed = instance 
    grid_seed = instance + grid_start_seed
    c_settings = {"gamma0":x[0],"gamma":x[1],"tau":x[2],"thetaC":x[3],"swarmCount":x[4],"feedback":feedback,'eta':2000,"seed":instance+grid_start_seed,"sample_strategy":sample_strategy,"size":gridsize,"Usp":1500,"P(FP)":P_fp,"P(FN)":P_fn}
    s_settings = {"right_dec":right_dec,"fill_ratio":fill_ratio,"offset_f":0.04,"check_interval":10,"autoexit":1,"run_full":run_full}
    settings = {"reevaluation":reevaluation,"word_creation_seed":world_creation_seed,"grid_seed":grid_seed ,"description":desc}

    job.job_setup(c_settings=c_settings,s_settings=s_settings,settings=settings,world_creation_seed=world_creation_seed,grid_seed=grid_seed,fill_ratio=fill_ratio,gridsize=gridsize,grid_ = grid)
    job.run_webots_instance(port=1234+instance)
    fitness = job.get_fitness()
    #Matei: change folders below according to your path
    job.move_results("/home/thiemenrug/Documents/_temp/",f"parallel_{run_dir}/Instance_{instance}")
    job.remove_run_dir()
    del x
    return fitness


def launch_batch(batch_size,workers, x_, run_dir , feedback ,fill_ratio ,robots,grid=None ,size = 5 ,desc="None"):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as process_executor:  
        futures = [process_executor.submit(launch_instance, x_,i,run_dir,feedback,fill_ratio,robots,grid,size,desc) for i in range(batch_size)]
        [future.result() for future in futures]
    remove_dir(f"jobfiles/Run_{run_dir}")


# Configuration for the simulation or experiment

# False Positive Rate (P_fp) -> used in Environment::getSample(double x, double y)
# Description: Define the probability percentage of false positives during sampling (only used for sample_strategy = 2)
P_fp = 0 

# False Negative Rate (P_fn) -> used in Environment::getSample(double x, double y)
# Description: Define the probability percentage of false negatives during sampling (only used for sample_strategy = 2)
P_fn = 0 

# Sampling Strategy
# Description: Define the sampling strategy to use; 0 = perfect sampling according to world file. 1 = using distributions, 2 = using FP and FN
sample_strategy = 1  

# Grid Start Seed
# Description: Define the seed value for initializing the random number generator of the seed
# This ensures that results can be reproduced across runs.
grid_start_seed = 400  

# Full Run Flag
# Description: Flag to indicate whether to run the full experiment or stop upon making a final decision
run_full = 0  # Example: set to 0 for a partial run, 1 for a full run

# Batch Size
# Description: Define the number of simulations to process in a single batch.
# Example: 10 simulations per batch.
batch_size = 10 

# Number of Threads
# Description: Define the number of threads to use for parallel processing.
# Example: 3 threads for concurrent processing.
number_of_thread = 3  # Example: set to 3 for three threads

feedback = 1 #0 for no feedback, 1 positive feedback

# Input Values of the robot state machine (I send them before)
x = [7860, 10725, 3778, 55, 381]  

launch_batch(10, workers=number_of_thread, x_ = x, run_dir = 1, feedback = 0, fill_ratio=0.48, robots=5)