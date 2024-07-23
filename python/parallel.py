import numpy as np
from webots import WebotsEvaluation
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent.futures
def launch_instance(x,reevaluation = 0,run_dir=0,feedback =0,fill_ratio = 0.48,n_robots= 5):
    instance = reevaluation
    if fill_ratio > .5:
        right_dec=1
    else:
        right_dec = 0
    job = WebotsEvaluation(run = run_dir,instance = reevaluation,robots=n_robots)
    
    world_creation_seed = instance
    grid_seed = instance
    c_settings = {"gamma0":x[0],"gamma":x[1],"tau":x[2],"thetaC":x[3],"swarmCount":x[4],"feedback":feedback,'eta':700}
    s_settings = {"right_dec":right_dec,"fill_ratio":fill_ratio,"offset_f":0.04,"check_interval":10,"autoexit":1}

    settings = {"reevaluation":reevaluation,"word_creation_seed":world_creation_seed,"grid_seed":grid_seed}
    job.job_setup(c_settings=c_settings,s_settings=s_settings,settings=settings,world_creation_seed=world_creation_seed,grid_seed=grid_seed,fill_ratio=0.48,gridsize=5)
    job.run_webots_instance()
    fitness = job.get_fitness()
    job.move_results("/home/thiemenrug/Desktop/",f"parallel_{run_dir}/Instance_{instance}")
    job.remove_run_dir()
    del x
    return fitness


def launch_batch(batch_size,workers,x_,run_dir,feedback,fill_ratio,robots):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as process_executor:  
        futures = [process_executor.submit(launch_instance, x_,i,run_dir,feedback,fill_ratio,robots) for i in range(batch_size)]
        [future.result() for future in futures]


x_=[5000,10000,3000,60,300]
for feedback in [2]:
    launch_batch(batch_size=100,workers=8,x_=x_,run_dir=feedback,feedback=feedback,fill_ratio=0.48,robots=4)