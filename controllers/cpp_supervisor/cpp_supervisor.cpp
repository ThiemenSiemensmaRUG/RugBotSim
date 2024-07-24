#include <webots/Supervisor.hpp>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>
#include <cstdlib>  // For getenv function
#include <filesystem>
#include <algorithm> // for std::all_of
#include <unistd.h>   
#include "supervisor_settings.hh"
#include <thread>
#include <chrono>

using namespace webots;

#define TIME_MAX 1200
#define TIME_STEP 20

#include <iostream>
#include <cmath>  // For std::abs
double calculateFitness(int final_decision, int correct_decision, double fill_ratio, double correct_fill_ratio, double time, double t_max, double fill_offset) {
    if (fill_offset == 0) {
        std::cerr << "Error: fill_offset cannot be zero." << std::endl;
        return 100;  // Return an error value or handle it appropriately
    }

    double final_d_error = 0;

    if (time < 1) { 
        time = t_max; 
    }
    if (time == 0) {
        std::cerr << "Error: time cannot be zero." << std::endl;
        return 100;  // Return an error value or handle it appropriately
    }

    if ((final_decision != correct_decision) &&(final_decision !=-1)) {
        final_d_error = 5.0;
    } else {
        final_d_error = std::abs(time / t_max);
    }

    double fill_error = std::abs(fill_ratio - correct_fill_ratio) / fill_offset;
    double total_error = final_d_error * fill_error;

    std::cout << "Final Decision Error: " << final_d_error << std::endl;
    std::cout << "Fill Ratio Error: " << fill_error << std::endl;
    std::cout << "Total Error: " << total_error << std::endl;

    return total_error;
}



SupervisorSettings settings{};
int pos = 0;
int T_MAX = 1200;
int print_time_interval = settings.values[3];
bool uniform_decision = false;

// Function to clean up and delete the Supervisor instance
static int cleanUp(Supervisor *supervisor) {
  delete supervisor;
  return 0;
}

int main() {
  try {
    // Create a Supervisor instance
    Supervisor *supervisor = new Supervisor();
    std::vector<Node*> robots;
    std::string rov_r = "r";
    int start_itt = 0;

    // Loop to gather robot nodes from the world
    while (start_itt <= 10) {
      std::string temp = rov_r + std::to_string(start_itt);
      
      // Check if the robot node exists
      Node* robotNode = supervisor->getFromDef(temp);
      if (robotNode != nullptr) {
        robots.push_back(robotNode);
        start_itt++;
      } else {
        break;
      }
    }

    // Gather translation fields and customData fields for each robot
    std::vector<Field*> positions;
    std::vector<Field*> customData;
    for (Node* robot : robots) {
      positions.push_back(robot->getField("translation"));
      customData.push_back(robot->getField("customData"));
    }

    std::vector<int> states(robots.size(), -1);

    // Seed the random number generator
    srand(1);
    std::mt19937 gen(10); // Standard mersenne_twister_engine seeded with rd()
    std::uniform_real_distribution<> dis(0.05, 0.95);

    std::cout << "MAIN SUPERVISOR LOOP" << '\n';
    bool show_info = false;

    // Main simulation loop
    while (supervisor->step(TIME_STEP) != -1) {
      const double t = supervisor->getTime();

      if ((static_cast<int>(t) % print_time_interval == 0) && show_info && (t > 50.0)) {
        std::cout<<"showing info"<<std::endl;
        show_info = false;
        for (long unsigned int i = 0; i < robots.size(); i++) {
          Field* data = customData[i];
          const std::string data_rov = data->getSFString();
          pos = data_rov.find_last_of(",");
          int str_len = (int) data_rov.length();
          states[i] = std::stoi(data_rov.substr(pos+1,str_len-1)) ; 
        }
      }
      for (long unsigned int i = 0; i < robots.size(); i++) {
        if ((states[i] != -1)) {
          uniform_decision = true; 
        }
        else {
          uniform_decision = false; 
          break;
        }

      }



      // Check and adjust the position of robots based on proximity
      for (Node* rov1 : robots) {
        const double *values = rov1->getField("translation")->getSFVec3f();
        for (Node* rov : robots) {
          if (rov != rov1) {
            const double *values_other = rov->getField("translation")->getSFVec3f();
            double dist = std::sqrt(std::pow(values_other[0] - values[0], 2) + std::pow(values_other[2] - values[2], 2));
            if (dist < 0.03) {
              const double RANDOM[3] = {dis(gen), 0.0125, dis(gen)};
              rov->getField("translation")->setSFVec3f(RANDOM);
              rov->resetPhysics();
            }
          }
        }
      }

      if ((int(t) % print_time_interval != 0)) {
        show_info = true;
      }

      if ((t > T_MAX) || uniform_decision ) {
        supervisor->simulationSetMode(Supervisor::SIMULATION_MODE_PAUSE);
        // Pause simulation and exit
        double fitness = 0;
        std::cout << "---final values-------" << std::endl;
        for (size_t i = 0; i < robots.size(); i++) {
          Field* data = customData[i];
          const std::string data_rov = data->getSFString();
          std::cout << data_rov << '\n';

          std::vector<std::string> v;
          std::stringstream ss(data_rov);
          std::string substr;
          while (getline(ss, substr, ',')) {
            v.push_back(substr);
          }
          std::cout<<"Calculating fitness for robot = "<<i <<" with time = "<< std::stod(v[17]) << std::endl;
          fitness += calculateFitness(states[i], settings.values[0], std::stod(v[10]), settings.values[1], std::stod(v[17]), static_cast<double>(T_MAX), settings.values[2]);
        }

        // Define the path for the fitness output file
        const char* pPath = std::getenv("WB_WORKING_DIR");
        std::string filePath = (pPath != nullptr) ? std::string(pPath) + "/fitness.txt" : "fitness.txt";
        std::cout << filePath << '\n';
        std::ofstream myfile(filePath);
        if (myfile.is_open()) {
          myfile << fitness;
          myfile.close();
          std::cout << "wrote fitness: " << fitness << std::endl;
        } else {
          std::cerr << "Unable to open file to write fitness" << std::endl;
        }

        std::cout << "Quiting simulation" << '\n';
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        supervisor->simulationSetMode(Supervisor::SIMULATION_MODE_PAUSE);


        if (static_cast<int>(settings.values[4]) == 1) {
          supervisor->simulationQuit(0);
        }

        if (supervisor->step(TIME_STEP) == -1) {
          return cleanUp(supervisor);
        }
        // Clean up and delete the Supervisor instance


      }
    }
    delete supervisor;
    return 0;


  } catch (const std::exception &e) {
    std::cerr << "Exception: " << e.what() << std::endl;
    return 0;
  } catch (...) {
    std::cerr << "Unknown exception occurred" << std::endl;
    return 0;
  }
  return 0;
}