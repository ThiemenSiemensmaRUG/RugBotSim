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

#define ACCURACY 1

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
    void set_custom_data();
    void print_custom_data();
    void pause(int *pauseCount);
    void SetSimulationVariables();
   private:

  
    double sample_pause = 0.0;
    double sample_length = 1.0;  // Sample length in seconds
    ControllerSettings settings;
    RugRobot robot;
    Radio_Rover radio;
    std::vector<int> pos;
    std::vector<double> numbers;


    std::vector<std::vector<double>> samples;
    Sampling sampler;
};

/**
 * @brief Executes the main algorithm loop for the robot's inspection controller.
 */
void StateMachine::run() {
    robot.setCustomData("");
    // Assuming settings.values contains values that need to be converted to int
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
                if(robot.state == 0){intersample_time+=TIME_STEP;}
                //if(robot.state == 3){intersample_time = 0;}
                if(robot.state == 6){intersample_time = 0;}
                if(robot.state == 7){intersample_time = 0;}
    
                break;
            

            case STATE_OBS: {

                intersample_time = 0;
                pauseCount = 500;
                pos = roundToNearestX(robot.getPos(), ACCURACY);
                sampler.getSample(pos[0] - 500, pos[1] - 500);                
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
    sampler.initializer(static_cast<int>(settings.values[0]), static_cast<int>(settings.values[1]));
    tau = static_cast<int>(settings.values[2]);

}

void StateMachine::set_custom_data(){
    robot.setCustomData(std::to_string((double)robot.d_robot->getTime()) +
                    "," + std::string(robot.d_robot->getName().substr(1)) +
                    "," + std::to_string(robot.getPos()[0]) +
                    "," + std::to_string(robot.getPos()[1]) +
                    "," + std::to_string(sampler.lastSample) 
                    );
}

void StateMachine::print_custom_data(){
    std::cout << robot.getCustomData() << '\n';
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

#endif  // INCLUDED_STATEMACHINE_HH_
