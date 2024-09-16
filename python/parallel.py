import numpy as np
from webots import WebotsEvaluation
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent.futures
from utils import *




def launch_instance(x,reevaluation = 0,run_dir=0,feedback =0,fill_ratio = 0.48,n_robots= 5,grid = None,gridsize = 5):
    instance = reevaluation
    if fill_ratio > .5:
        right_dec=1
    else:
        right_dec = 0
    job = WebotsEvaluation(run = run_dir,instance = reevaluation,robots=n_robots)
    
    world_creation_seed = instance
    grid_seed = instance
    c_settings = {"gamma0":x[0],"gamma":x[1],"tau":x[2],"thetaC":x[3],"swarmCount":x[4],"feedback":feedback,'eta':eta,"seed":instance+10,"sample_strategy":sample_strategy,"size":gridsize,"Usp":Usp,"P(FP)":P_fp,"P(FN)":P_fn}
    s_settings = {"right_dec":right_dec,"fill_ratio":fill_ratio,"offset_f":0.04,"check_interval":10,"autoexit":1,"run_full":0}
    settings = {"reevaluation":reevaluation,"word_creation_seed":world_creation_seed,"grid_seed":grid_seed + 300 + grid_start_seed}

    job.job_setup(c_settings=c_settings,s_settings=s_settings,settings=settings,world_creation_seed=world_creation_seed,grid_seed=grid_seed,fill_ratio=fill_ratio,gridsize=gridsize,grid_ = grid)
    job.run_webots_instance(port=1234+instance)
    fitness = job.get_fitness()
    job.move_results("/home/thiemenrug/Desktop/",f"parallel_{run_dir}/Instance_{instance}")
    job.remove_run_dir()
    del x
    return fitness


def launch_batch(batch_size,workers,x_,run_dir,feedback,fill_ratio,robots,grid=None,size = 5):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as process_executor:  
        futures = [process_executor.submit(launch_instance, x_,i,run_dir,feedback,fill_ratio,robots,grid,size) for i in range(batch_size)]
        [future.result() for future in futures]



M1 = diagonal_matrix()
M2 = stripe_matrix()
M3 = block_diagonal_matrix()
M4 = organized_alternating_matrix()
M5 = random_matrix()

eta = 1250
Usp = 2000
P_fp = 0
P_fn = 0
sample_strategy = 0
run_directory = 9
grid_start_seed = 100

number_of_thread = 6

x = [10000, 19116, 3000, 50, 400]



"""Code below runs the parallel launches for comparision of Umin, Uplus and Us over different fll-ratios"""

for feedback_strategy in [0]:#0 for Umin, 1 Uplus, 2 Us
    run_directory+=1
    launch_batch(100,number_of_thread,x,run_directory,feedback_strategy,0.48,5)



