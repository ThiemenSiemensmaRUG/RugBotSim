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

/// @brief edit these values for extra output file or speed up simulations
bool writeExtraOutput = false;
int print_time_interval = 20;
bool auto_exit_sim = true;
int correct_dec = 0;
double penalty = 0.0;
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
  bool exit_sim = false;

  std::ifstream file("supervisor_settings.txt");
  int z;
  for (int i = 0; i < 5; i++) {
      std::string line;
      std::getline(file, line);
      const char *cstr = line.c_str();
      z = std::atof(cstr);
      std::cout <<z <<'\n';
      if (i == 0){writeExtraOutput = z;}
      if (i == 1){print_time_interval = z;}
      if (i == 2){auto_exit_sim = z;}
      if (i == 3){correct_dec = z;}
      if (i == 4){penalty = z;}
      }

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

  // Initialize arrays for states and decision times for each robot
  int states[robots.size()];
  for (int i = 1; i < robots.size(); i++) {
    states[i] == -1;
  }
  int dec_times[robots.size()];
  for (int i = 1; i < robots.size(); i++) {
    dec_times[i] == 0;
  }

  // Seed the random number generator
  srand(0);
  std::mt19937 gen(10); // Standard mersenne_twister_engine seeded with rd()
  std::uniform_real_distribution<> dis(0.05, 0.95);
  std::cout << "first random number"  << rand() <<'\n';
  std::cout << "first RV number"  << dis(gen) <<'\n';
  
  // Print initial pose information for each robot
  for (Node* robot : robots) {
    std::cout << "init pose " << robot->getDef() << "=" << *robot->getField("translation")->getSFVec3f() << '\n';
  }

  // Define the path for the extra output file
  std::string ExtraFileString = (pPath != nullptr) ? std::string(pPath) + "/extraOutput.txt" : "extraOutput.txt";

  // Open and check the status of the extra output file
  std::ofstream extraFile;
  extraFile.open(ExtraFileString);

  std::cout << "MAIN SUPERVISOR LOOP" << '\n';
  bool show_info = false;

  // Main simulation loop
  while (supervisor->step(TIME_STEP) != -1) {
    const double t = supervisor->getTime();

    // Write extra output data to file at specified intervals
    if (writeExtraOutput) {
      for (int i = 0; i < robots.size(); i++) {
        Field* data = customData[i];
        const std::string data_rov = data->getSFString();
        std::vector<std::string> v;
        std::stringstream ss(data_rov);
        while (ss.good()) {
          std::string substr;
          getline(ss, substr, ',');
          v.push_back(substr);
          
        }
        Node* rov = robots[i];
        
        const double *values = rov->getField("translation")->getSFVec3f();
        extraFile  << t << ',' << i + 1 << ',' << i + 1 << ',' << values[0] << ',' << values[2] << ',' << " " << ',' << v[2] << ',' << v[3] << ',' << v[0] << ',' << v[1] << ','<<v[6]<<',' << v[7] << ',' << v[8] << ',' << v[10] << ',' << v[11] << '\n';
      }
    }

    // Print information at specified time intervals
    if (((int(t) % print_time_interval == 0) && (show_info))) {
      std::cout << "time = " << t << '\n';
      show_info = false;
      for (int i = 0; i < robots.size(); i++) {
        if (exit_sim == false) {
          Field* data = customData[i];
          const std::string data_rov = data->getSFString();
          std::cout << data_rov << '\n';
          states[i] = std::stoi(data_rov.substr(9,2));
          int pos = data_rov.find_last_of(",");
          int str_len = (int) data_rov.length();
          dec_times[i] = std::stoi(data_rov.substr(pos+1,str_len-1)) / 1000; 
        }
      }
      std::cout << "----------" << '\n';

      for (int i = 0; i < robots.size(); i++) {
        if ((dec_times[i] != 0)) {
          exit_sim = true; 
        }
        if (dec_times[i] == 0) {
          exit_sim = false; 
          break;
        }
        std::cout << "time = " << dec_times[i] << " for " << i << "exit = " << exit_sim << '\n';
      }
      std::cout << "exit sim =" << exit_sim << '\n';

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
    }
    
    // Set flag for showing info at next interval
    if ((int(t) % print_time_interval != 0)) {
      show_info = true;
    }

    // Check simulation termination conditions
    if ((t > TIME_MAX) || (exit_sim && auto_exit_sim)) {
      if (t > TIME_MAX) {
        std::cout << "TIMED OUT" << '\n';
      }
      if (exit_sim) {
        std::cout << "BAYES DECISION MADE" << '\n';
      }

      float max = dec_times[0];
      float fitness = 0.0;
      int right_dec = true;
      std::cout << "EXIT SIMULATION" << '\n';
      int total_alpha = 0;
      int total_samples =0;
      for (int i = 0; i < robots.size(); i++) {
        Field* data = customData[i];
        const std::string data_rov = data->getSFString();
        states[i] = std::stoi(data_rov.substr(9,2));
        std::cout << data_rov << '\n';
        std::vector<std::string> v;
        std::stringstream ss(data_rov);
        while (ss.good()) {
          std::string substr;
          getline(ss, substr, ',');
          v.push_back(substr);
        }
        total_alpha+= +std::stoi(v[5]);
        total_samples += + std::stoi(v[6]);
        float estimated_f = ((float) total_alpha) / ((float) total_samples);
        float corr_f_fac = 1.0+  std::abs((estimated_f - 0.48))/0.04;
        int pos = data_rov.find_last_of(",");
        int str_len = (int) data_rov.length();
        dec_times[i] = std::stoi(data_rov.substr(pos+1,str_len-1)) / 1000; 
        std::cout <<"Estimated f of r"<<i<<" = "<<estimated_f <<'\n';
        std::cout << "Correction factor for f= "<<  corr_f_fac<<'\n';
        if ((states[i] == correct_dec) || (states[i]==-1) ) {
          
          if(states[i] == -1){
            std::cout<<"Time Fitness r"<<i<<" = 1.0"<<'\n';
            fitness+=(1.0);//* corr_f_fac);
            std::cout<<"Correcteds Fitness r"<<i<<" = "<<1.0 <<'\n';

          }
          else{
            std::cout<<"Time Fitness r"<<i<<" = "<<((float) dec_times[i] )/ TIME_MAX<<'\n';
            fitness+= (((float) dec_times[i] )/ TIME_MAX ) ;//* corr_f_fac  ;  
            std::cout<<"Correcteds Fitness r"<<i<<" = "<< (((float) dec_times[i] )/ TIME_MAX )  <<'\n';
          }

        }
        else{
          std::cout<<"Fitness r"<<i<<" = "<<penalty<<'\n';
          right_dec = false;
          fitness+=penalty ;//* corr_f_fac;
          std::cout<<"Correcteds Fitness r"<<i<<" = "<< penalty  <<'\n';
          
        }

        
        if (dec_times[i] > max) {
          max = (float) dec_times[i];

        }
      std::cout<<'\n';

      }

      

      std::cout << "Uniform Correctness = " << right_dec << '\n';

      std::cout << "Total Cost Value = " << fitness << '\n';
      


     
      // Define the path for the fitness output file
      std::string filePath = (pPath != nullptr) ? std::string(pPath) + "/local_fitness.txt" : "local_fitness.txt";
      std::cout << filePath << '\n';
      std::ofstream myfile;
      myfile.open(filePath);
      myfile << std::to_string(fitness);
      myfile.close();
      
      // Close the extra output file and remove if not required
      extraFile.close();
      if (!writeExtraOutput) {
        remove(ExtraFileString.c_str());
      }
      std::cout << "written fitness -> "<< fitness << '\n';
      
      // Pause simulation and exit
      supervisor->simulationSetMode(supervisor->SIMULATION_MODE_PAUSE);
      if(auto_exit_sim){
        std::cout<<"Quiting simulation" << '\n';
    
        supervisor->simulationQuit(0);
      }
    }
    
    // Step the simulation

    if (supervisor->step(TIME_STEP) == -1) {
      return cleanUp(supervisor);
    }
  }

  // Clean up and delete the Supervisor instance
  delete supervisor;
  return 0;
}
