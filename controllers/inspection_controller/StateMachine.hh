#ifndef INCLUDED_STATEMACHINE_HH_
#define INCLUDED_STATEMACHINE_HH_
#include <cmath>
#include <complex>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>

#include "RugBot.hh"
#include "controller_settings.hh"
#include "utils/Filtering.hh"
#include "radio.hh"
#include "utils/Sampling.hh"

typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;



#define ACCURACY 100

// Structure to hold x, y, and sample value
struct SampleData {
    int x;
    int y;
    double sample_value;

    SampleData(int x, int y, double sample_value)
        : x(x), y(y), sample_value(sample_value) {}
};

class StateMachine {
   public:
    enum AlgoStates {
        STATE_RW,    // State: Random Walk
        STATE_OBS,   // State: Observe Color
        STATE_PAUSE,  // etc....
        RESET
    };

    AlgoStates states = STATE_RW;
    // Time step for the simulation
    enum { TIME_STEP = 20 };
    int tau = 250;
    int time = 0;
    int intersample_time = 0;
    int pauseCount = 1000; 

    StateMachine()
        : settings(),
          robot(TIME_STEP),
          radio(robot.d_robot, TIME_STEP) {};
    void run();
    void update(SampleData newSample);
    void set_custom_data();
    void print_custom_data();
    void pause(int *pauseCount);
    void SetSimulationVariables();
        // Send a sample to other robots
    void SendSample(const SampleData &data);
    void updateCoverage(int x, int y);

    // Receive a sample from other robots
    void RecvSample();
   private:

  
    double sample_pause = 0.0;
    double sample_length = 1.0;  // Sample length in seconds
    ControllerSettings settings;
    RugRobot robot;
    Sampling sampler;
    Radio_Rover radio;
    std::vector<SampleData> all_samples;
    std::vector<int> pos;
    // Dynamically adjust the grid size based on the ACCURACY
    int gridSize = (int) (1000 / ACCURACY);
    double coverage = 0.0;
    int filledSquares = 0;
    std::vector<std::vector<bool>> grid = std::vector<std::vector<bool>>(gridSize, std::vector<bool>(gridSize, false));

    
};

/**
 * @brief Executes the main algorithm loop for the robot's inspection controller.
 */
void StateMachine::run() {
    robot.setCustomData("");

    settings.readSettings();
    SetSimulationVariables();
    while (robot.d_robot->step(TIME_STEP) != -1) {
        switch (states) {
            case STATE_RW: {
                
                if (((intersample_time - tau) > 0) ) {
                    pause(&pauseCount);
                    break;
                }
                robot.RandomWalk();
                RecvSample();
                if(robot.state == 0){intersample_time+=TIME_STEP;}
                if(robot.state == 6){intersample_time = 0;}
                if(robot.state == 7){intersample_time = 0;}
    
                break;
            

            case STATE_OBS: {

                intersample_time = 0;
                pauseCount = 500;
                pos = roundToNearestX(robot.getPos(), 1);
                sampler.getSample(pos[0], pos[1]);                
 
                // Directly store the gathered sample
                SampleData newSample(pos[0], pos[1], sampler.lastSample);
                update(newSample);

                // Send the sample to other robots
                SendSample(newSample);
                set_custom_data();
                print_custom_data();
                
                states = STATE_RW;
                break;
            }

            case STATE_PAUSE:
                break;
            case RESET:
                try {
                    // Reset state logic goes here
                    std::cout << "Resetting state..." << std::endl;
                    states = STATE_RW;  // Transition back to a default state
                    //recvSample();
                } catch (const std::exception &e) {
                    std::cerr << "Error in RESET state: " << e.what() << std::endl;
                    // Handle further errors or perform additional cleanup
                }
                break;

            default:
                std::cerr << "Unknown state: " << states << std::endl;
                states = RESET;  // Transition to RESET state to handle unknown state
                break;
        }
        
        
}}}

void StateMachine::SetSimulationVariables(){
    sampler.initializer(static_cast<int>(settings.values[0]), static_cast<int>(settings.values[1]), 1);
    tau = static_cast<int>(settings.values[2]);

}

void StateMachine::update(SampleData newSample){
    all_samples.push_back(newSample);
    updateCoverage(newSample.x, newSample.y);
}

void StateMachine::set_custom_data(){
    robot.setCustomData(std::to_string((double)robot.d_robot->getTime()) +
                    "," + std::string(robot.d_robot->getName().substr(1)) +
                    "," + std::to_string(robot.getPos()[0]) +
                    "," + std::to_string(robot.getPos()[1]) +
                    "," + std::to_string(sampler.lastSample) +
                    "," + std::to_string(all_samples.size()) +
                    "," + std::to_string(coverage)
                    );
}

void StateMachine::print_custom_data(){
    std::cout << robot.getCustomData() << '\n';
}

void StateMachine::updateCoverage(int x, int y) {
    // Calculate the scaling factor to map coordinates to the grid


    // Map the coordinates to the grid using accuracy
    int grid_x = static_cast<int>(x / ACCURACY);
    int grid_y = static_cast<int>(y / ACCURACY);
 
    if (!grid[grid_x][grid_y]) {
        grid[grid_x][grid_y] = true;
        ++filledSquares;
    }
    

    // Calculate the total number of grid cells
    int totalCells = grid[0].size() * grid[0].size();  
    // Calculate and return the filled percentage
    coverage =  static_cast<double>((double)(filledSquares) / (double) totalCells * 100.0 );
}

void StateMachine::pause(int *pause_Time) {
    // Stop the robot's movement
    robot.setSpeed(0, 0);
    
    // Check if pause time has elapsed, if yes, transition to observation state
    if (*pause_Time <= TIME_STEP) {
        states = STATE_OBS;
        return;
    }
    
    // Decrease pause time based on the time step
    *pause_Time = *pause_Time - 1 * TIME_STEP;
}

// Sending sample data to other robots
void StateMachine::SendSample(const SampleData &data) {
    // Send x, y, and sample_value as a list of integers
    int sample[3];
    sample[0] = data.x;                          // x coordinate
    sample[1] = data.y;                          // y coordinate
    sample[2] = static_cast<int>(data.sample_value * 1000000);  // sample value scaled (multiply by 1000000 for precision)
    radio.sendMessage(sample, sizeof(sample)); // Send 3 integers (x, y, scaled sample_value)

}

// Receiving sample data from other robots
void StateMachine::RecvSample() {
    // Get the messages from the radio receiver
    std::vector<int> messages = radio.getMessages();

    // Process each received message in groups of 3 (x, y, sample_value)
    for (size_t i = 0; i < messages.size(); i += 3) {
        // Ensure there are at least 3 values to process
        if (i + 2 < messages.size()) {
            int x = messages[i];
            int y = messages[i + 1];
            double sample_value = (double) (messages[i + 2] / 1000000.0 ); // Convert back to original sample value

            // Create a SampleData object from received values
            SampleData receivedSample(x, y, sample_value);

            // Optionally, store the received sample
            update(receivedSample);

        }
    }
}

#endif  // INCLUDED_STATEMACHINE_HH_
