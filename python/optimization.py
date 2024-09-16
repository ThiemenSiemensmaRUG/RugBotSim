import numpy as np
from webots import WebotsEvaluation
from PSO import PSO

run_dir =9


def rosenbrock(x,particle=0,iteration=0,reevaluation=0): 
    value = sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
    return value 

def cost_function(x,particle=0,iteration=0,reevaluation=0):
    job = WebotsEvaluation(run = run_dir,instance = particle * reevaluation,robots=5)
    world_creation_seed = (particle+1) * (iteration + 1) * reevaluation
    grid_seed = reevaluation * (iteration +1)
    robot_seed = grid_seed

    c_settings = {"gamma0":x[0],"gamma":x[1],"tau":x[2],"thetaC":x[3],"swarmCount":x[4],"feedback":0,"eta":1250,"seed":robot_seed,"use_distribution":1,"size":5,"Usp":2000,"P(FP)":0,"P(FN)":0}
    s_settings = {"right_dec":0,"fill_ratio":0.48,"offset_f":0.04,"check_interval":20,"autoexit":1,"run_full":0}
    settings = {"particle":particle,"iteration":iteration,"reevaluation":reevaluation,"word_creation_seed":world_creation_seed,"grid_seed":grid_seed}
    job.job_setup(c_settings=c_settings,s_settings=s_settings,settings=settings,world_creation_seed=world_creation_seed,grid_seed=grid_seed,fill_ratio=0.48)
    port = 1234+ particle + (reevaluation % 10)
    job.run_webots_instance(port=port)
    fitness = job.get_fitness()
    if fitness == 100:
        log_file_path = f"error_log_{run_dir}.txt"
        with open(log_file_path, "a") as log_file:
            log_file.write(f"Error: Particle {particle}, Iteration {iteration}, Reevaluation {reevaluation}, port{port}\n")
    else:
        log_file_path = f"error_log_{run_dir}.txt"
        with open(log_file_path, "a") as log_file:
            log_file.write(f"Processed: Particle {particle}, Iteration {iteration}, Reevaluation {reevaluation}, port{port}\n")
    job.move_results("/home/thiemenrug/Desktop/",f"pso_{run_dir}/I{iteration}/P{particle}/R{reevaluation}")
    job.remove_run_dir()
    del job

    return fitness


bounds = np.array([[0,20000],[0,20000],[1000,6000],[50,150],[0,500]])
number_of_particles =25
number_of_iterations = 50
number_of_reevaluations =10
number_of_init_evaluations = 10
percentage_reevaluation = 0.2
number_of_threads = 4 #be careful above 5, might cause crashes

run_dir =8

pso = PSO(1,0,[1,0.4],0.75,0.75,bounds,0,cost_function,number_of_iterations,number_of_particles,number_of_reevaluations,percentage_reevaluation,number_of_init_evaluations)
pso.pso_threaded(number_of_threads)
pso.webots_data.to_csv(f"jobfiles/pso_{run_dir}.csv")


run_dir =9

pso = PSO(2,0,[1,0.4],0.75,0.75,bounds,0,cost_function,number_of_iterations,number_of_particles,number_of_reevaluations,percentage_reevaluation,number_of_init_evaluations)
pso.pso_threaded(number_of_threads)
pso.webots_data.to_csv(f"jobfiles/pso_{run_dir}.csv")
