# RugBot

Swarm of miniature robots. Simulated version of RugBot in Webots.

## Overview

This repository simulates the RugBot robot used for surface inspection tasks at the Distributed Robotic Systems Lab, Groningen. It is part of the ENTEG institute, specifically the DTPA department.

### Distributed Robotic Systems Lab, Groningen

The Distributed Robotic Systems Lab at Groningen focuses on developing advanced robotic systems for distributed tasks. This repository contains the simulated version of the robot used in various experiments.

## Repository Details

The `main` branch is dedicated to developing core functionalities for the RugBot simulation, including output-related tasks for the Webots robotic simulator (such as setting up environments).

### Branches

- Each branch focuses on specific algorithm development.
- The `main` branch serves as the base for merging updates to basic functionalities.

## Installation

To set up your environment for RugBot simulation, this repository includes a `setup.sh` script located at the root of the repository. The script will automate the installation of necessary dependencies, including Webots, GitHub Desktop, Google Chrome, and Python packages, and configure VS Code with essential extensions.

### Running the `setup.sh` Script


### Running the `setup.sh` Script

To set up the RugBot simulation environment, run the `setup.sh` script located in the root directory of the repository. This script automates the installation of all necessary dependencies and tools required for the simulation. 

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

## Usage

Details on how to use and interact with the simulation will be included in this section.

## Contributing

Information on how to contribute to the project will be provided here, including guidelines for pull requests and the code of conduct.

## License

This project is licensed under the [License Name] - details about the license will be provided here.

## Contact

For questions or further information, please contact:

- [Bahar Haghighat](mailto:bahar.haghighat@yourdomain.com) (PI, Distributed Robotic Systems Lab, Groningen)
- [Thiemen Siemensma](mailto:thiemen.siemensma@yourdomain.com) (PhD Student, Distributed Robotic Systems Lab, Groningen)
