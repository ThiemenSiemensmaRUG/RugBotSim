#  Optimization of Collective Bayesian Decision-Making in a Swarm of Miniaturized Vibration-Sensing Robots

Submitted to Swarm Intelligence journal - Siemensma et al. 

## Overview

This repository simulated the Bayesian decision making process. It contains PSO optimization, grid search for Us, and other simulation results. Moreover, the analysis of experiments is done using the same post-processing scripts as during simulations. The folders within this repository are organized as follows:

### 📁 controllers
Code for the Webots robot controller and supervisor controllers.  
- **compile.sh**: Script used to compile both controllers.  
- Each robot within the simulation runs an instance of the inspection controller.

### 📁 jobfiles
Stores the temporary simulation files.  
- These files are cleaned and moved after the simulation is finished.  

### 📁 measurements
Contains files used for calibrating the experimental setup to match the simulation.

### 📁 protos
Contains proto files of the simulation, which define the models of the robots.

### 📁 python
Contains all Python code.  
- **analyse_experiments.py**: Script used for calibrating the experimental setup to the simulation as described within the paper.
- **analyse_parallel.py**: Script used for calibrating the experimental setup to the simulation as described within the paper.
- **analyse_pso.py**: Used for analyzing PSO results
- **calibration.py**: Script used for calibrating the experimental setup to the simulation as described within the paper.
- **optimization.py**: Used for running the PSO optimization
- **parallel.py**: Used for running the batch results, such as grid search Us, fill-ratio results, and multi-robot results
- **PSO.py**: PSO library
- **utils.py**: Utilities library
- **webots_log_processor.py**: Functionallity to analyse Webots or real experimental results
- **webots.py**: Contains file to run Webots
- **webotsWorldCreation.py**: Library functionality to create Webots worlds 


## Installation

To set up your environment for simulation, this repository includes a `setup.sh` script located at the root of the repository. The script will automate the installation of necessary dependencies, including Webots, GitHub Desktop, Google Chrome, and Python packages, and configure VS Code with essential extensions.

### Running the `setup.sh` Script

To set up the RugBot simulation environment, run the `setup.sh` script located in the root directory of the repository. This script automates the installation of all necessary dependencies and tools required for the simulation. Start with a clean Ubuntu 22.04.1 LTS installation.

#### Steps to Execute the Script

1. Open a terminal and navigate to the root directory of the RugBot repository.
2. Make the script executable (if not already done).
3. Execute the script.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

The script will perform the following actions (optional is not required for functionality):
- Update the package list for your system.
- Install Visual Studio Code.
- Download and install Google Chrome (optional).
- Set up and install GitHub Desktop (optional).
- Install the DisplayLink driver (optional).
- Install Webots for robotic simulation.
- Install Python and the necessary packages (numpy, pandas, scipy, matplotlib, pyserial).
- Configure Visual Studio Code with essential extensions for Python and C/C++ development.
- Install LaTeX for rendering plots in Python.

After the script completes, you will be prompted to restart your machine to apply all changes.


## Contact

For questions or further information, please contact:

- [Bahar Haghighat](mailto:bahar.haghighat@yourdomain.com) (PI, DAISY Lab, Groningen)
- [Thiemen Siemensma](mailto:thiemen.siemensma@yourdomain.com) (PhD Student, DAISY Lab, Groningen)
