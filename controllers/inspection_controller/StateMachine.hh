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
        STATE_PAUSE  // etc....
    };

    AlgoStates states = STATE_RW;
    // Time step for the simulation
    enum { TIME_STEP = 20 };

    StateMachine()
        : settings(),
          robot(TIME_STEP),
          radio(robot.d_robot, TIME_STEP) {};
    void run();
    void set_custom_data();
    void print_custom_data();

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
    pos = roundToNearestX(robot.getPos(), ACCURACY);
    robot.setCustomData("");
    // Assuming settings.values contains values that need to be converted to int
    settings.readSettings();
    sampler.initializer(static_cast<int>(settings.values[0]), static_cast<int>(settings.values[1]));

    while (robot.d_robot->step(TIME_STEP) != -1) {
        switch (states) {
            case STATE_RW: {
                if (robot.RandomWalk() == 1) {
                    states = STATE_OBS;
                }
             
                }
                break;
            

            case STATE_OBS: {
                sample_pause += TIME_STEP;
                if (sample_pause < (sample_length * 1000)) {
                    break;
                }
                sample_pause = 0.0;
                pos = roundToNearestX(robot.getPos(), ACCURACY);
                sampler.getSample(pos[0] - 500, pos[1] - 500);                
                set_custom_data();
                print_custom_data();

                states = STATE_RW;
                break;
            }

            case STATE_PAUSE:
                break;
        }
        
        
}}

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

#endif  // INCLUDED_STATEMACHINE_HH_
