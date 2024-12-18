import os
import subprocess
import time
from webotsWorldCreation import createWorld
import shutil

class WebotsEvaluation():

    def __init__(self, run_dir = 1, instance = 1, n_robots = 4):
        self.run = run_dir
        self.instance = instance
        self.robots = n_robots
        self.run_dir = f"jobfiles/Run_{self.run}/"
        self.instance_dir = f"{self.run_dir}Instance_{self.instance}/"

        

        pass



    def check_main_directory(self):
        # Get the current working directory
        current_dir = os.getcwd()
        
        # Check if the current directory ends with 'RugBotSim'
        if not current_dir.endswith("RugBotSim"):
            raise OSError(f"Error: Current directory '{current_dir}' is not the main repo directory needed for starting simulations'.")
        else:
            print(f"Current directory is correct: {current_dir}")

    def create_instance_dir(self):
        try:
            os.makedirs(self.instance_dir, exist_ok=True)
            print(f"Created instance directory {self.instance_dir}\n")
        except OSError as e:
            print(f"Error creating instance directory {self.instance_dir}: {e}")
        pass

    def run_webots_instance(self):
        # Method to run a Webots instance with given parameters
        subprocess.check_call(['.././run_webots.sh', str(self.run), str(self.instance), 
                               str(self.robots)])
        print(os.getcwd())
        os.chdir("../../")
        print(os.getcwd())

    def delete_instance_dir(self):
        if os.path.exists(self.instance_dir):
            shutil.rmtree(self.instance_dir)
            print(f"Deleted run directory: {self.instance_dir}")
        pass
    
    def delete_run_dir(self):
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)
            print(f"Deleted run directory: {self.run_dir}")
        pass
    

    def job_setup(self, c_settings={}, s_settings={}, settings={}):
        # Step 1: Create the instance directory for simulation files
        self.check_main_directory()
        self.create_instance_dir()

        # Step 2: Generate a world object to create Webots world files
        world = createWorld(
            run=self.run,
            instance=self.instance,
            seed=1,
            name=f"world_{self.instance}",
            n_robots=self.robots
        )

        # Step 3: Save controller and supervisor settings in the instance directory
        world.save_settings(c_settings, s_settings)

        # Step 4: Create the .wbt world file
        world.create_world()

        # Step 5: Save general simulation settings to a settings.txt file in the instance directory
        setup = f"{self.instance_dir}/settings.txt"
        with open(setup, 'w') as file:
            for value in [settings.values()]:
                file.write(str(value) + '\n')

        # Step 6: Pause briefly before proceeding (for stability)
        time.sleep(1)

        # Step 7: Change the working directory to the run directory
        os.chdir(self.run_dir)

        pass

    




for _, instance in enumerate(range(1,3)):
    eval = WebotsEvaluation(n_robots=10, instance=instance)

    c_settings = {"isDamaged":_,"modeNumber":1,"time between samples[ms]":250}
    s_settings = {"temp":1.0}
    


    eval.job_setup(c_settings=c_settings,s_settings=s_settings )
    eval.run_webots_instance()
    #eval.delete_run_dir()
    del eval