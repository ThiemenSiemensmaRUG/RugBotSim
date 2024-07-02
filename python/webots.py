import os
import subprocess
import time
from webotsWorldCreation import createWorld

class WebotsEvaluation():

    def __init__(self):
        self.run =1
        self.instance =1
        self.robots = 4
        pass
    def run_webots_instance(self):
        # Method to run a Webots instance with given parameters
        subprocess.check_call(['.././run_webots.sh', str(self.run), str(self.instance), 
                               str(self.robots)])
        print(os.getcwd())
        os.chdir("../../")
        print(os.getcwd())

    def job_setup(self,c_settings= {},s_settings = {},settings={}):
        

        run_dir = f"jobfiles/Run_{self.run}/"
        os.makedirs(os.path.dirname(f"{run_dir}I_{self.instance}/"), exist_ok=True)

        world = createWorld(self.instance,self.instance,f"world_{self.instance}",self.robots)
        world.save_settings(run_dir,c_settings,s_settings)
        world.create_world()
        setup =  f"{run_dir}I_{self.instance}/settings.txt"

        with open(setup, 'w') as file:
            for value in [settings.values()]:
                file.write(str(value) + '\n')
        time.sleep(1)

        os.chdir(run_dir)  # Changing directory to the run directory
        


        pass

robots= [4]
learningrates =[1]
for i in range(1):

    x = WebotsEvaluation()
    x.instance = 4
    x.robots = 6

    c_settings = {"a0":1.0,"a1":0.96,"b0":0.98,"b1":0.98,"learning_rate":learningrates[i],"upper_freq":100.0}
    s_settings = {"temp":1.0}
    x.job_setup(c_settings=c_settings,s_settings=s_settings)
    x.run_webots_instance()
    
    del x