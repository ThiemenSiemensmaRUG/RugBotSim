#include <webots/Supervisor.hpp>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>
#include <cstdlib>  // For getenv function
#include <filesystem>
#include <unistd.h>   

using namespace webots;

#define TIME_MAX 1200
#define TIME_STEP 20





int print_time_interval = 10;

// Get the working directory path
char *pPath = getenv("WB_WORKING_DIR");

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
        std::cout << temp << '\n';
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

  std::cout<<robots.size()<<'\n';
  // Seed the random number generator
  srand(1);
  std::mt19937 gen(10); // Standard mersenne_twister_engine seeded with rd()
  std::uniform_real_distribution<> dis(0.05, 0.95);
  std::cout << "first random number"  << rand() <<'\n';
  std::cout << "first RV number"  << dis(gen) <<'\n';
  
  // Print initial pose information for each robot
  for (Node* robot : robots) {
    std::cout << "init pose " << robot->getDef() << "=" << *robot->getField("translation")->getSFVec3f() << '\n';
  }
  


  std::cout << "MAIN SUPERVISOR LOOP" << '\n';
  bool show_info = false;
  std::ofstream outputFile;
  outputFile.open("data_rov.txt");
    // Check if the file was successfully opened
  if (!outputFile.is_open()) {
    std::cerr << "Error: Unable to open data_rov.txt for writing" << std::endl;
    return 1; // Return an error code or handle the error as needed
  } else {
    std::cout << "File data_rov.txt opened successfully" << std::endl;
  }
  // Main simulation loop
  while (supervisor->step(TIME_STEP) != -1) {
    const double t = supervisor->getTime();


    // Print information at specified time intervals
    if(( (int(t) % print_time_interval) == 0) && (show_info)) {
      std::cout << "time = " << t << '\n';
      show_info= false;
      for (int i = 0; i < robots.size(); i++) {

        Field* data = customData[i];
        const std::string data_rov = data->getSFString();
        std::cout << data_rov << '\n';

        int pos = data_rov.find_last_of(",");
        int str_len = (int) data_rov.length();
        
        outputFile <<t<<","<< data_rov << '\n';
        outputFile.flush(); // Ensure all buffered data is written to file
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



}};