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
#include "Environment.hh"
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
    int sample = 0;
    int d_f = -1;
    // Time step for the simulation
    enum { TIME_STEP = 20 };

    Algorithm1() : settings(),robot(TIME_STEP), beta(1,1),radio(robot.d_robot,TIME_STEP),environ("world.txt") {};

    void run();
    void print_data(int print_bool);
    void recvSample();
    void sendSample(int sample);
    void pause(int *pauseCount);

private:
    ControllerSettings settings;
    RugRobot robot;
    BetaDistribution beta;
    Radio_Rover radio;
    Environment environ;

};

void Algorithm1::run() {
    std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;

    robot.setCustomData("");
    
    settings.readSettings();

    robot.setRWTimeGenParams(settings.values[0],settings.values[1]);
    tau = settings.values[2];
    robot.CA_Threshold = settings.values[3];
    while(robot.d_robot->step(TIME_STEP) != -1) {
        time = (int) robot.d_robot->getTime();

        if (robot.state == 0){intersample_time+=TIME_STEP;}
        
        switch(states) {
            case STATE_RW:
                recvSample();
                if ((intersample_time-tau)>0){
                    pause(&pauseCount);
                    break;
                } 
                robot.RandomWalk();
                break;

            case STATE_OBS:
                pauseCount = tau;
                sample = environ.getSample(robot.getPos()[0],robot.getPos()[1],0);
                beta.update(sample);
                print_data(1);
                sendSample(sample);
                states = STATE_RW; 
                break;

            case RESET:
                //reset state

                break;
        }
        //print_data(0);
        
    }
}

void Algorithm1::print_data(int print_bool) {//0 for not printing and only in custom data, 1 for also printing.
if(robot.d_robot->getTime() > 5) {
    std::string customData = 
        std::to_string(print_bool) + "," +
        std::to_string((int) robot.d_robot->getTime()) + "," +
        std::string(robot.d_robot->getName().substr(1, 1)) + "," +
        std::to_string(beta.getBelief()) + "," +
        std::to_string(beta.alpha) + "," +
        std::to_string(beta.beta) + "," +
        std::to_string(beta.getMean()) + "," +
        std::to_string(robot.getPos()[0]) + "," +
        std::to_string(robot.getPos()[1]);

    // Set the custom data
    robot.setCustomData(customData);

    if (print_bool){
        std::cout << customData << std::endl;}
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
            beta.update(sample);
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














