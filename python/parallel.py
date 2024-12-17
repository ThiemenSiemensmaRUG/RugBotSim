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
    c_settings = {"gamma0":x[0],"gamma":x[1],"tau":x[2],"thetaC":x[3],"swarmCount":x[4],"feedback":feedback,'eta':eta,"seed":instance+grid_start_seed,"sample_strategy":sample_strategy,"size":gridsize,"Usp":Usp,"P(FP)":P_fp,"P(FN)":P_fn}
    s_settings = {"right_dec":right_dec,"fill_ratio":fill_ratio,"offset_f":0.04,"check_interval":10,"autoexit":1,"run_full":run_full}
    settings = {"reevaluation":reevaluation,"word_creation_seed":world_creation_seed,"grid_seed":grid_seed ,"description":desc}

    job.job_setup(c_settings=c_settings,s_settings=s_settings,settings=settings,world_creation_seed=world_creation_seed,grid_seed=grid_seed,fill_ratio=fill_ratio,gridsize=gridsize,grid_ = grid)
    job.run_webots_instance(port=1234+instance)
    fitness = job.get_fitness()
    job.move_results("/home/thiemenrug/Documents/_temp/",f"parallel_{run_dir}/Instance_{instance}")
    job.remove_run_dir()
    del x
    return fitness


def launch_batch(batch_size,workers,x_,run_dir,feedback,fill_ratio,robots,grid=None,size = 5,desc="None"):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as process_executor:  
        futures = [process_executor.submit(launch_instance, x_,i,run_dir,feedback,fill_ratio,robots,grid,size,desc) for i in range(batch_size)]
        [future.result() for future in futures]
    remove_dir(f"jobfiles/Run_{run_dir}")


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




CAL_GRID = np.array([
                    [0, 1, 0, 1, 0],  # Row corresponding to y=1.0 to y=0.8
                    [1, 0, 0, 1, 0],  # Row corresponding to y=0.8 to y=0.6
                    [1, 0, 1, 0, 1],  # Row corresponding to y=0.6 to y=0.4
                    [0, 1, 1, 0, 1],  # Row corresponding to y=0.4 to y=0.2
                    [1, 0, 0, 1, 0]   # Row corresponding to y=0.2 to y=0.0
                ])

print(calculate_morans_I(CAL_GRID),entropy(CAL_GRID))

P_fp = 0
P_fn = 0
sample_strategy = 1
grid_start_seed = 400
run_full=0
batch_size = 100
number_of_thread = 3


eta = 1500
Usp = 2000
x = [7860, 10725 , 3778  , 55,381]



# run_directory = 10 #Start dir for calibration us
# grid_start_seed = 400
# for eta in [750,1000,1250,1500,1750,2000,2250,2500]:
#     for Usp in [1000,2000,3000,4000]:
#         launch_batch(batch_size=batch_size,workers=number_of_thread,x_=x,run_dir=run_directory,feedback=2,fill_ratio=0.48,robots=5,size=5,desc=f"Calibration Us")   
#         run_directory+=1

# # """Code below runs the parallel launches for comparision of Umin, Uplus and Us over different fll-ratios"""

# eta = 1500
# Usp = 2000
# run_directory = 50 #start dir
# grid_start_seed = 400
# for fill_ratio in [0.44,0.48,0.52,0.56]: #different grid sizes

#     for feedback in [0,1,2]:#Umin, Uplus and Us
#         launch_batch(batch_size=batch_size,workers=number_of_thread,x_=x,run_dir=run_directory,feedback=feedback,fill_ratio=fill_ratio,robots=5,size=5,desc=f"f{fill_ratio},feedbac strategy{feedback}")   
#         run_directory+=1


# # # """------------------------------------------------"""

# run_directory = 100 # start dir
# # # """Below code runs over multiple robots 2*6*3*100 = 3600 simulations"""
# grid_start_seed = 400
# for fill_ratio in [0.48]:
#     for n_robots in [10,9,8,7,6,5]:
#         for feedback in [0,1,2]:#Umin, Uplus and Us
#             launch_batch(batch_size=batch_size,workers=1,x_=x,run_dir=run_directory,feedback=feedback,fill_ratio=fill_ratio,robots=n_robots,size=5,desc=f"f{fill_ratio},feedbac strategy{feedback}")   
#             run_directory+=1



batch_size=100
x_empirical =  [7500,15000,2000,50,320]

run_directory = 150 #Start dir
grid_start_seed = 400
for nrovs in [5,6,7,8,9,10]:
    for pattern in [M1,M2,M3,M4,M5,M1_46,M2_46,M3_46,M4_46,M5_46]:
        for pos in [x,x_empirical]:
        
            for feedback in [0,1,2]:#Umin, Uplus and Us
                launch_batch(batch_size=batch_size,workers=1,x_=pos,run_dir=run_directory,feedback=feedback,fill_ratio=0.48,robots=nrovs,grid=pattern,size=pattern.shape[0],desc=f"Moran Index with n_robots {5}, feedback {feedback}",)   
                run_directory+=1


