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

#include "RugBot.hh"
#include "Environment.hh"
#include "radio.hh"
#include "controller_settings.hh"

typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;






class Algorithm1 {
public:
    enum AlgoStates {
        STATE_RW,  // State: Random Walk
        STATE_OBS, // State: Observe Color
        STATE_PAUSE // etc....
    };


    AlgoStates states = STATE_RW;


    // Time step for the simulation
    enum { TIME_STEP = 20 };

    Algorithm1() : settings(),robot(TIME_STEP),radio(robot.d_robot,TIME_STEP) {};

    void run();
    void recvSample();
    void sendSample(int sample);

private:
    ControllerSettings settings;
    RugRobot robot;
    Environment environ;
    Radio_Rover radio;
    std::vector<int> pos;
    int sample_ = 0;

};

void Algorithm1::run() {
    //std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;
   
    robot.setCustomData("");
    settings.readSettings();

    while(robot.d_robot->step(TIME_STEP) != -1) {
        
        switch(states) {

            case STATE_RW:

                if(robot.RandomWalk()==1){
                    states = STATE_OBS;
                }

                break;

            case STATE_OBS:
                sample_ = environ.getSample(robot.getPos()[0], robot.getPos()[1]);
                states = STATE_RW;                  
                break;


            case STATE_PAUSE:
                // Pause logic here
                break;
        }
        if(robot.d_robot->getTime()>5){
        robot.setCustomData( std::to_string((int) robot.d_robot->getTime())+
        ","+std::string(robot.d_robot->getName().substr(1,1)) );
        }
    }
}


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














