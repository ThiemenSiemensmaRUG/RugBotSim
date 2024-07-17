#ifndef INCLUDED_ALGORITHM1_HH_
#define INCLUDED_ALGORITHM1_HH_
#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <vector>
#include <cmath>
#include <utility>
#include <filesystem>
#include "filtering.hh"
#include "RugBot.hh"
#include "radio.hh"
#include "controller_settings.hh"
#include "BetaDistribution.hh"
typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;






class Algorithm1 {
public:
    enum AlgoStates {
        STATE_RW,  // State: Random Walk
        STATE_OBS, // State: Observe Color
        RESET, //reset state
    };


    AlgoStates states = STATE_RW;


    int tau = 1000;
    int time = 0;
    int intersample_time =0;
    int pauseCount = tau; 


    // Time step for the simulation
    enum { TIME_STEP = 20 };

    Algorithm1() : settings(),robot(TIME_STEP), beta(1,1),radio(robot.d_robot,TIME_STEP) {};

    void run();
    void recvSample();
    void sendSample(int sample);
    void pause(int *pauseCount);

private:
    ControllerSettings settings;
    RugRobot robot;
    BetaDistribution beta;
    Radio_Rover radio;
    std::vector<int> pos;


};

void Algorithm1::run() {
    //std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;
    pos = roundToNearest10(robot.getPos());
    robot.setCustomData("");
    settings.readSettings();

    while(robot.d_robot->step(TIME_STEP) != -1) {
  
        time = (int) robot.d_robot->getTime();
        intersample_time+=TIME_STEP;
        switch(states) {
            case STATE_RW:
                if ((intersample_time-tau)>0){
                    pause(&pauseCount);
                    break;
                } 
                robot.RandomWalk();
                break;

            case STATE_OBS:
                pauseCount = tau;

                beta.update(1);
                std::cout<<beta.alpha<<","<<beta.beta<<'\n';
                std::cout<<beta.getCDF(0.5)<<'\n';
                states = STATE_RW; 
                break;

                // Pause logic here
                break;
            case RESET:
                //reset state

                break;
        }
        if(robot.d_robot->getTime()>5){
        robot.setCustomData( std::to_string((int) robot.d_robot->getTime())+
        ","+std::string(robot.d_robot->getName().substr(1,1)) );
        }
    }
}


void Algorithm1::pause(int *pause_Time) {
    // Stop the robot's movement
    robot.setSpeed(0, 0);
    
    // Check if pause time has elapsed, if yes, transition to observation state
    if (*pause_Time <= 0) {
        states = STATE_OBS;
        intersample_time = 0;
        return;
    }
    
    // Decrease pause time based on the time step
    *pause_Time = *pause_Time - 1 * TIME_STEP;
};

void Algorithm1::recvSample(){
    std::vector<int> messages = radio.getMessages();
        // Process received messages
        for (int sample : messages) {
            //Do something
        }
}

void Algorithm1::sendSample(int sample){

    // Determine the message to send based on decision flag or observation color
    int const *message;

    message = &sample;
    // Send the message
    radio.sendMessage(message, sizeof(message));

}


#endif // INCLUDED_ALGORITHM1_HH_














