import numpy as np
import pandas as pd

import concurrent.futures
# Top-level function to evaluate a particle initially
def evaluate_particle_initial(particle, iteration,r, seed, sigma, objective_func):
    if r ==1001:
        particle.current_values = []

    value = objective_func(particle.position, particle=particle.number, iteration=iteration, reevaluation=r)
    if float(value) ==100.0:
        return particle
    particle.re_eval_value = value
    particle.current_value = add_noise(particle.re_eval_value,seed,iteration+1,particle.number,r,sigma)
    particle.current_values.append(particle.current_value)
    return particle

# Top-level function to reevaluate a particle
def reevaluate_particle(particle, iteration, r, seed, sigma, objective_func):
    value =objective_func(particle.position, particle=particle.number, iteration=iteration, reevaluation=r)
    if float(value) ==100.0:
        return particle
    particle.re_eval_value = value
    particle.current_value = add_noise(particle.re_eval_value,seed,iteration+1,particle.number,r,sigma)
    particle.current_values.append(particle.current_value)
    return particle


def add_noise(value,seed, iteration,number,evaluation,sigma):
    np.random.seed(seed=(seed * iteration * number * evaluation))
    value = value * (1 + np.random.normal(0, sigma))
    return value 

def fitness(values):
    if len(values) == 0:
        return 100
    fitness = np.mean(values) + np.std(values)
    return fitness


class PSO:
    def __init__(self,seed=0, sigma=0.1, weight_max_min=[1,.4], c1=0.5, c2=0.5, bounds=None, success_threshold=0.01, objective_func=None, iterations=10, particles = 20,reevaluations =15,evaluation_percentage = 0.6,initial_evaluations=1):
        self.sigma = sigma
        self.seed = seed
        np.random.seed(seed=self.seed)
        self.rng = np.random.default_rng(seed=self.seed)
        
        self.iterations = iterations
        self.num_particles = particles

        self.weigths = np.linspace(weight_max_min[0],weight_max_min[1],self.iterations)
        self.c1 = c1 # particle = [future.result() for future in futures]
        self.c2 = c2
        if bounds is None:
            print("Bounds is None")
            quit()
        self.bounds = bounds
        self.dimensions = self.bounds.shape[0]
        self.success_threshold = success_threshold
        self.objective_func = objective_func
    
        self.global_best_position = np.random.uniform(low=self.bounds[:, 0], high=self.bounds[:, 1], size=(self.dimensions,))
        self.global_best_value = np.inf

        self.re_percentage = evaluation_percentage
        self.reevaluations = reevaluations
        self.initials_vals = initial_evaluations   

        self.angle = np.pi/4
        self.apply_rotation = False
        self.particles = [Particle(self.bounds,i+1) for i in range(self.num_particles)]
        
        self.output_data = pd.DataFrame()
        self.webots_data = pd.DataFrame()
        self.output_list = []

    def update_particles(self,iteration):
        #extend webots data df
        for particle in self.particles:
            self.extend_webots_data(iteration,particle)
        self.webots_data.to_csv("intermediate_result.csv")
        
        for particle in self.particles:
            particle.current_value = fitness(particle.current_values.copy())   
            
            if (abs(particle.current_value) < particle.best_value):
                particle.best_position = particle.position.copy()
                particle.best_value = abs(particle.current_value)
            
            if (abs(particle.current_value) < self.global_best_value):
                self.global_best_position = particle.position.copy()
                self.global_best_value = abs(particle.current_value)
            

        for particle in self.particles:
            r1, r2 =self.rng.random((2,self.dimensions)) 

            cognitive_component = self.c1 * r1 * (particle.best_position - particle.position)
            social_component = self.c2 * r2 * (self.global_best_position - particle.position)
            
            particle.velocity = self.weigths[iteration] * particle.velocity + cognitive_component + social_component

        for particle in self.particles:
            particle.position += particle.velocity.copy()
            if self.apply_rotation and self.dimensions ==2:
                theta = np.random.uniform(-self.angle, self.angle)  # Random rotation angle for each iteration
                rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
                particle.position = rotation_matrix.dot(particle.position)

            particle.position = np.clip(particle.position, particle.bounds[:, 0], particle.bounds[:, 1])
            
            

    def pso(self):
        # Loop over the total number of iterations
        for i in range(self.iterations):
            
            # Loop over each particle in the list of particles
            for particle in self.particles:
                # Initialize an empty list to store current evaluation values for the particle
                particle.current_values = []
                for r in range(1,self.initials_vals+1):

                    
                    # Evaluate the objective function at the particle's current position without reevaluation
                    particle.re_eval_value  = self.objective_func(particle.position, particle=particle.number, iteration=i, reevaluation=r+1000)
                    
                    # Modify the evaluation value by adding normally distributed noise scaled by sigma
    
                    particle.current_value = add_noise(particle.re_eval_value,self.seed,i+1,particle.number,r+1000,self.sigma)
      
                    # Append the reevaluated value to the particle's current values list               
                    particle.current_values.append(particle.current_value)

        
            particle.current_value = fitness(particle.current_values.copy())   
                # Extend a DataFrame with the particle's data for the current iteration and reevaluation step (0)
                #self.extend_df(particle, i, 0, i * particle.number)
            
            # Select the top particles based on their current evaluation values
            # Sorting particles by their current_value attribute and selecting the top percentage defined by re_percentage
            top_particles = sorted(self.particles, key=lambda x: x.current_value)[:int(self.num_particles * self.re_percentage)]
            
            # Loop over each of the top particles for further reevaluation
            for particle in top_particles:
                
                # Perform additional reevaluations as specified by self.reevaluations
                for r in range(2, self.reevaluations + 2):
                    
                    # Re-evaluate the objective function for the particle
                    particle.re_eval_value = self.objective_func(particle.position, particle=particle.number, iteration=i, reevaluation=r)
                    
                    # Modify the reevaluated value by adding normally distributed noise scaled by sigma
                    particle.current_value = add_noise(particle.re_eval_value,self.seed,i+1,particle.number,r,self.sigma)
                    
                    # Append the new reevaluated value to the particle's current values list
                    particle.current_values.append(particle.current_value)
                    
                    # Extend a DataFrame with the particle's data for the current iteration and reevaluation step
                    #self.extend_df(particle, i, r, i * particle.number * r + 1)
               
            
            # Update particles' attributes based on the current iteration (e.g., position, velocity)
            self.update_particles(i)
            self.extend_short_list(i)
            
        return
    
    def pso_threaded(self,min_processes=4):#be carefull using to many processes, causes conflicts and crashes in webots
        num_processes = min(min_processes, len(self.particles))  # Number of processes

        for i in range(self.iterations):
            # Initial evaluations
            
            for r in range(1,self.initials_vals+1):
                futures = []
                with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as process_executor:
                   
                    futures = [process_executor.submit(evaluate_particle_initial, particle, i, r+1000, self.seed, self.sigma, self.objective_func) for particle in self.particles]
                    self.particles = [future.result() for future in futures]
                

            for particle in self.particles:
                particle.current_value = fitness(particle.current_values.copy())   

            # Select top particles for reevaluation
            top_indices = sorted(range(len(self.particles)), key=lambda idx: self.particles[idx].current_value)[:int(self.num_particles * self.re_percentage)]
            top_particles = [self.particles[idx] for idx in top_indices]
            
            # Reevaluations
            for r in range(2,self.reevaluations+2):
                with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as process_executor:
                    reevaluation_futures = [process_executor.submit(reevaluate_particle, particle, i, r, self.seed, self.sigma, self.objective_func) for particle in top_particles]
                    reevaluated_particles = [future.result() for future in reevaluation_futures]
                
                # Update the top_particles with the reevaluated results
                for j, particle in enumerate(top_particles):
                    top_particles[j] = reevaluated_particles[j]

                # Update self.particles with the reevaluated particles
                for idx, particle in zip(top_indices, top_particles):
                    self.particles[idx] = particle
                
            # Update particles
            self.update_particles(i)
            self.extend_short_list(i)
            self.webots_data.to_csv("temporary_output.csv")
            
    
    def extend_short_list(self,iteration):
        mean_p_b = sum(particle.best_value for particle in self.particles) / len(self.particles)
        self.output_list.append([iteration,self.global_best_value,mean_p_b,self.global_best_position])
    

    def extend_df(self,particle,i,r,seed):
        new_data = {
            'Iteration': [i],
            "Particle":[particle.number],
            "Evaluation":[r],
            "Seed":seed,
            "Fitness":[particle.re_eval_value],
            "p_best_val":[particle.best_value],
            "g_best_val":[self.global_best_value],
            'position': [particle.position.copy()],
            "velocity":[particle.velocity.copy()],
            "g_position":[self.global_best_position],
            
        }
        new_df = pd.DataFrame(data =new_data)
        self.output_data = pd.concat([self.output_data, new_df], ignore_index=True)

    def extend_webots_data(self,i,particle):
        new_data = {
            'Iteration': [i],
            "Particle":[particle.number],
            "Seed":self.seed,
            "Fitness_vals":[particle.current_values],
            "p_best_val":[particle.best_value],
            "g_best_val":[self.global_best_value],
            'position': [particle.position.copy()],
            "velocity":[particle.velocity.copy()],
            "g_position":[self.global_best_position],
            
        }
        new_df = pd.DataFrame(data =new_data)
        self.webots_data = pd.concat([self.webots_data, new_df], ignore_index=True)


class Particle:
    def __init__(self, bounds, particle_num): 
        self.number = particle_num
        self.iteration_num = 0
        self.reeval_num = 0
        self.bounds = bounds
        self.dimensions = self.bounds.shape[0]
        
        self.position = np.random.uniform(low=self.bounds[:, 0], high=self.bounds[:, 1], size=(self.dimensions,))
        self.velocity = np.zeros_like(self.position)
        self.best_position = np.copy(self.position)
        self.best_value = np.inf
        self.current_value = np.inf
        self.re_eval_value = np.inf
        self.current_values = []

    

