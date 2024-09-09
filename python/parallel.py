import numpy as np
from webots import WebotsEvaluation
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent.futures
def launch_instance(x,reevaluation = 0,run_dir=0,feedback =0,fill_ratio = 0.48,n_robots= 5,grid = None):
    instance = reevaluation
    if fill_ratio > .5:
        right_dec=1
    else:
        right_dec = 0
    job = WebotsEvaluation(run = run_dir,instance = reevaluation,robots=n_robots)
    
    world_creation_seed = instance
    grid_seed = instance
    c_settings = {"gamma0":x[0],"gamma":x[1],"tau":x[2],"thetaC":x[3],"swarmCount":x[4],"feedback":feedback,'eta':700,"seed":instance}
    s_settings = {"right_dec":right_dec,"fill_ratio":fill_ratio,"offset_f":0.04,"check_interval":10,"autoexit":1,"run_full":1}

    settings = {"reevaluation":reevaluation,"word_creation_seed":world_creation_seed,"grid_seed":grid_seed + 300}
    job.job_setup(c_settings=c_settings,s_settings=s_settings,settings=settings,world_creation_seed=world_creation_seed,grid_seed=grid_seed,fill_ratio=0.48,gridsize=5,grid_ = grid)
    job.run_webots_instance(port=1234+instance)
    fitness = job.get_fitness()
    job.move_results("/home/thiemenrug/Desktop/",f"parallel_{run_dir}/Instance_{instance}")
    job.remove_run_dir()
    del x
    return fitness


def launch_batch(batch_size,workers,x_,run_dir,feedback,fill_ratio,robots,grid=None):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as process_executor:  
        futures = [process_executor.submit(launch_instance, x_,i,run_dir,feedback,fill_ratio,robots,grid) for i in range(batch_size)]
        [future.result() for future in futures]



M1 = np.array([[1,1,0,0,0],[1,1,1,0,0],[0,1,1,1,0],[0,0,1,1,1],[0,0,0,0,1]])#diagonal
M2 = np.array([[1,1,1,1,1],[1,1,1,1,1],[1,1,0,0,0],[0,0,0,0,0],[0,0,0,0,0]])#stripe
M3 = np.array([[0,0,1,1,1],[0,0,1,1,1],[0,0,1,1,1],[1,0,0,0,0],[1,1,0,0,0]])#block diagonal
M4 = np.array([[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0]])#organized
M5 = np.array([[0,0,0,1,1],[0,1,1,0,0],[0,0,1,1,1],[0,1,1,0,0],[1,1,0,1,0]])#random


x_ = [ 7500, 15000, 2000, 60, 85*5]

launch_batch(3,3,x_,10,0,0.48,5)


# #x_=[420 ,14730  ,2078 ,   76,249]
# x_ = [ 5715, 19805,  2513, 51,305 ]
# grids = [M1,M2,M3,M4,M5]
# for feedback in [0,1,2]:
#     for run in range(5):
#         launch_batch(batch_size=100,workers=6,x_=x_,run_dir=run,feedback=0,fill_ratio=0.48,robots=5,grid=grids[run])