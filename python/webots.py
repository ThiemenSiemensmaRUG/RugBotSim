import os
import subprocess
import time
from webotsWorldCreation import createWorld
import shutil
import numpy

class WebotsEvaluation():

    def __init__(self,run,instance,robots):
        self.run =run
        self.instance =instance
        self.robots = robots
        pass

    def run_webots_instance(self, timeout=120, print_=False,port=1234):
        # Method to run a Webots instance with given parameters
        try:
            subprocess.check_call(['.././run_webots.sh', str(self.run), str(self.instance), 
                                   str(self.robots),str(port)], timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"Webots instance {self.instance} timed out after {timeout} seconds")
        
        if print_:
            print(os.getcwd())
        
        os.chdir("../../")
        
        if print_:
            print(os.getcwd())



    def job_setup(self,c_settings= {},s_settings = {},settings={},world_creation_seed = 1,grid_seed = 1,fill_ratio=0.48,gridsize = 5,grid_ = None):

        run_dir = f"jobfiles/Run_{self.run}/"
        os.makedirs(os.path.dirname(f"{run_dir}Instance_{self.instance}/"), exist_ok=True)
        print(os.getcwd())
        world = createWorld(self.instance,world_creation_seed,f"world_{self.instance}",self.robots)
        world.save_settings(run_dir,c_settings,s_settings)
        world.create_world()
        world.saveGrid(run_dir,size = gridsize,fill_ratio=fill_ratio,seed = grid_seed,grid_ = grid_)
        setup =  f"{run_dir}Instance_{self.instance}/settings.txt"
   
        with open(setup, 'w') as file:
            for key, value in settings.items():
                file.write(f"{key}: {value}\n")
        file.close()
        time.sleep(1)
        os.chdir(run_dir)  # Changing directory to the run directory

    def get_fitness(self):
        # Method to read the fitness value from fitness.txt file
        run_dir = f"jobfiles/Run_{self.run}/"
        fitness_file = f"{run_dir}Instance_{self.instance}/fitness.txt"
        if os.path.isfile(fitness_file):
            with open(fitness_file, 'r') as file:
                fitness_value = file.readline().strip()
            return float(fitness_value)
        else:
            return 100 #probably an error occurred 
   

    def move_results(self, output_folder, output_name):
        # Method to move the results to a specified folder
        run_dir = f"jobfiles/Run_{self.run}/"
        source_dir = f"{run_dir}Instance_{self.instance}"
        destination_dir = os.path.join(output_folder, output_name)
        
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, destination_dir,dirs_exist_ok=True)
            print(f"Results moved to {destination_dir}")
        else:
            raise FileNotFoundError(f"Source directory not found at {source_dir}")


    def remove_run_dir(self):
        # Method to delete the run directory
        run_dir = f"jobfiles/Run_{self.run}/"
        source_dir = f"{run_dir}Instance_{self.instance}"
        
        if os.path.exists(source_dir):
            shutil.rmtree(source_dir)
            
        else:
            raise FileNotFoundError(f"Source directory not found at {source_dir}")




