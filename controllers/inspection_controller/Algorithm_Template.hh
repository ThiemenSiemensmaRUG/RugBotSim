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

    enum feedbackStrategy {
        NON,
        POSITIVE,
        SOFT
    };

    feedbackStrategy feedback = POSITIVE;

    AlgoStates states = STATE_RW;


    int tau = 1000;
    int time = 0;
    int intersample_time =0;
    int pauseCount = 1000; 
    int sample = 0;
    int recvs = 0;
    int sends = 0;
    int message = 0;
    int d_f = -1;
    int min_swarmCount = 400;
    int SampleTime = 0;
    int decisionTime = 0;
    double p_c = 0.95;
    
    // Time step for the simulation
    enum { TIME_STEP = 20 };

    Algorithm1() : settings(),robot(TIME_STEP), beta(1,1),radio(robot.d_robot,TIME_STEP),environ("world.txt") {};

    void run();
    void print_data(int print_bool);
    void recvSample();
    void sendSample(int sample);
    void pause(int *pauseCount);
    void check_decision();
    int calculateMessage(int sample);
    void setSimulationSetup();

private:
    ControllerSettings settings;
    RugRobot robot;
    BetaDistribution beta;
    Radio_Rover radio;
    Environment environ;

    //random generator for softfeedback and softfeedback parameters
    std::random_device sf_rd;
    std::bernoulli_distribution soft_feedback;
    double delta = 0;
    double nu = 1250;

};

void Algorithm1::run() {
    std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;

    robot.setCustomData("");

    setSimulationSetup();

    while(robot.d_robot->step(TIME_STEP) != -1) {
        time = (int) robot.d_robot->getTime();

        if (robot.state == 0){intersample_time+=TIME_STEP;}
        
        switch(states) {
            case STATE_RW:
                recvSample();
                if ((intersample_time-tau)>0){
                    pause(&pauseCount);
                    SampleTime+=TIME_STEP;
                    break;
                } 
                robot.RandomWalk();
                break;

            case STATE_OBS:
                pauseCount = 1000;
                SampleTime+=TIME_STEP;
                sample = environ.getSample(robot.getPos()[0],robot.getPos()[1],0);
                beta.update(sample);
                beta.onboard_update(sample);
                check_decision();
                message = calculateMessage(sample);
                print_data(1);
                sendSample(message);
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
        std::to_string(sample) + "," +
        std::to_string(message) + "," +
        std::to_string(beta.getBelief()) + "," +
        std::to_string(beta.alpha) + "," +
        std::to_string(beta.beta) + "," +
        std::to_string(sends) + "," +
        std::to_string(recvs) + "," +
        std::to_string(beta.getMean()) + "," +
        std::to_string(beta.getOnboardMean()) + "," +
        std::to_string(robot.getPos()[0]) + "," +
        std::to_string(robot.getPos()[1]) + "," +
        std::to_string(robot.RWtime) + "," +
        std::to_string(robot.CAtime) + "," +
        std::to_string(SampleTime) + "," +
        std::to_string(decisionTime) + "," +
        std::to_string(d_f);

    // Set the custom data
    robot.setCustomData(customData);

    if (print_bool){
        std::cout << customData << std::endl;}
}


}

void Algorithm1::setSimulationSetup() {
    // Settings in the simulation based on input file
    settings.readSettings();
    
    // Print settings to show the values read
    std::cout << "Settings values: ";
    for (int value : settings.values) {
        std::cout << value << " ";
    }
    std::cout << std::endl;

    robot.setRWTimeGenParams(settings.values[0], settings.values[1]);
    tau = settings.values[2];
    robot.CA_Threshold = settings.values[3];
    min_swarmCount = settings.values[4];
    feedback = static_cast<feedbackStrategy>(settings.values[5]);

    // Print the updated values
    std::cout << "tau: " << tau << std::endl;
    std::cout << "CA_Threshold: " << robot.CA_Threshold << std::endl;
    std::cout << "min_swarmCount: " << min_swarmCount << std::endl;
    std::cout << "feedback: " << feedback << std::endl;
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
            recvs+=1;
            beta.update(sample);
        }
}

void Algorithm1::sendSample(int sample){

    // Determine the message to send based on decision flag or observation color
    int const *message;
    sends+=1;
    message = &sample;
    // Send the message
    radio.sendMessage(message, sizeof(message));

}

void Algorithm1::check_decision(){
    if ((recvs > min_swarmCount) && (d_f ==-1)){
        if (beta.getBelief() > p_c){d_f = 0; decisionTime = time;}
        if (beta.getBelief() < (1- p_c)) {d_f =1; decisionTime = time;}
    }

    return;
}

int Algorithm1::calculateMessage(int sample){
    if (feedback == NON){return sample;}

    if (feedback == POSITIVE){
        if (d_f == -1){return sample;}
        else{return d_f;}
    }

    if (feedback == SOFT){
        delta = exp(-1.0*nu * beta.getVariance()) * pow((1-beta.getBelief()),2);
        soft_feedback.param(std::bernoulli_distribution::param_type( delta * (1.0 - beta.getBelief()) + (1-delta) * sample ));
        return soft_feedback(sf_rd);
    }

}


#endif // INCLUDED_ALGORITHM1_HH_













