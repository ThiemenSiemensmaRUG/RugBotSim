#include <webots/Supervisor.hpp>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>
#include <cstdlib>  // For getenv function
#include <filesystem>
#include <unistd.h>   
#include "supervisor_settings.hh"

using namespace webots;

#define TIME_MAX 1200
#define TIME_STEP 20


double calculateFitness(int final_decision, int correct_decision, double fill_ratio, double correct_fill_ratio, double time , double t_max,double fill_offset) {
    double final_d_error =  std::abs(static_cast<double>(final_decision) - static_cast<double>(correct_decision))*5;

    if ( time ==0){time = t_max;}
    if (final_decision == -1){
      final_d_error = 1;
    }
    
    double fill_error = std::abs(fill_ratio - correct_fill_ratio) / fill_offset;
    double t_error = std::abs(time / t_max);
    double total_error = (final_d_error + fill_error )  + t_error;

    // Print errors and sum
    std::cout << "Final Decision Error: " << final_d_error << std::endl;
    std::cout << "Fill Ratio Error: " << fill_error << std::endl;
    std::cout << "Time Error: " << t_error << std::endl;
    std::cout << "Total Error: " << total_error << std::endl;

    return total_error;
}


SupervisorSettings settings{};



int pos = 0;
int T_MAX = 1200;


int print_time_interval = settings.values[3];
bool uniform_decision = false;
// Get the working directory path


// Function to clean up and delete the Supervisor instance
static int cleanUp(Supervisor *supervisor) {
  delete supervisor;
  return 0;
}

int main() {
  // Create a Supervisor instance
  Supervisor *supervisor = new Supervisor();
  std::vector<Node*> robots;
  std::string rov_r = "r";
   int start_itt = 0;
  // Loop to gather robot nodes from the world
  while (1) {
    try {  
      std::string temp = rov_r;
      temp.append(std::to_string(start_itt));
      
      // Check if the robot node exists
      if (supervisor->getFromDef(temp) != NULL) {
        robots.push_back(supervisor->getFromDef(temp));
        start_itt += 1;
      } else {
        break;
      }
      
      // Limit the loop to a maximum of 10 iterations
      if (start_itt > 10) {
        break;
      }
    } catch (const std::exception& e) {
      std::cerr << e.what() << '\n';
      break;
    }
  }

      



  // Gather translation fields and customData fields for each robot
  std::vector<Field*> positions;
  for (Node* robot : robots) {
    positions.push_back(robot->getField("translation"));
  }
  std::vector<Field*> customData;
  for (Node* robot : robots) {
    customData.push_back(robot->getField("customData"));
  }

  std::vector<int> states;
  for (Node* robot : robots){
    states.push_back(-1);
  }
  // Seed the random number generator
  srand(1);
  std::mt19937 gen(10); // Standard mersenne_twister_engine seeded with rd()
  std::uniform_real_distribution<> dis(0.05, 0.95);

  


  std::cout << "MAIN SUPERVISOR LOOP" << '\n';
  bool show_info = false;




  // Main simulation loop
  while (supervisor->step(TIME_STEP) != -1) {
    const double t = supervisor->getTime();

    if(( (int(t) % print_time_interval) == 0) && (show_info)) {
      show_info= false;
      for (int i = 0; i < robots.size(); i++) {

        Field* data = customData[i];
        const std::string data_rov = data->getSFString();
        pos = data_rov.find_last_of(",");

        states[i] = std::stoi(data_rov.substr(pos+1,((int) data_rov.length())-1));

        uniform_decision= true;
        for (int state : states) {
            if (state == -1) {
                uniform_decision = false;
                break;
            }
        }
        }
      }
     
      // Check and adjust the position of robots based on proximity
      for (Node* rov1 : robots) {
        const double *values = rov1->getField("translation")->getSFVec3f();
        for (Node* rov : robots) {
          if (rov != rov1) {
            const double *values_other = rov->getField("translation")->getSFVec3f();
            double dist = sqrt(pow(values_other[0] - values[0], 2) + pow(values_other[2] - values[2], 2));
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


  if((t>T_MAX) || (uniform_decision == true)){
    // Pause simulation and exit
    double fitness= 0;
    
    
    std::cout<<"---final values-------" << std::endl;
    for (int i = 0; i < robots.size(); i++) {

        Field* data = customData[i];
        const std::string data_rov = data->getSFString();
        std::cout <<data_rov<<'\n';
        std::vector<std::string> v;
        std::stringstream ss(data_rov);
        while (ss.good()) {
          std::string substr;
          getline(ss, substr, ',');
          v.push_back(substr);
        }
      
        fitness += calculateFitness(states[i],settings.values[0],std::stod(v[10]),settings.values[1], std::stod(v[17]),(double)T_MAX,settings.values[2]) ;
        
    }
    
    // Define the path for the fitness output file
    std::string filePath = (pPath != nullptr) ? std::string(pPath) + "/fitness.txt" : "fitness.txt";
    std::cout << filePath << '\n';
    std::ofstream myfile;
    myfile.open(filePath);
    myfile << std::to_string(fitness);
    myfile.close();
    std::cout << "wrote fitness:"<<fitness<<std::endl;
    std::cout<<"Quiting simulation" << '\n';
    supervisor->simulationSetMode(supervisor->SIMULATION_MODE_PAUSE);

    if ((int)settings.values[4] ==1){
      supervisor->simulationQuit(0);}

    if (supervisor->step(TIME_STEP) == -1) {
      return cleanUp(supervisor);
    }

    delete supervisor;
    return 0;
    }



}};