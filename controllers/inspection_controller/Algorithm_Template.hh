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

#include <random>
#include <algorithm>
#include "radio.hh"
#include "controller_settings.hh"
#include "BetaDistribution.hh"
#include "Environment.hh"
typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;



#define TIME_MAX 1200


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
    double Us_exponent = 2.0;
 
    // Time step for the simulation
    enum { TIME_STEP = 20 };

    Algorithm1() : settings(),robot(TIME_STEP), beta(1,1),radio(robot.d_robot,TIME_STEP),environ("world.txt") {};

    ~Algorithm1() {
        // Destructor body can be left empty if no special cleanup is needed.
        // If your members have their own destructors, they will be called automatically.
    }
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
    std::default_random_engine sf_rd;
    std::bernoulli_distribution soft_feedback;
    double delta = 0;
    double eta = 1250;

};

void Algorithm1::run() {
    std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;

    robot.setCustomData("");

    setSimulationSetup();

    while(robot.d_robot->step(robot.d_robot->getBasicTimeStep()) != -1) {
        time = (int) robot.d_robot->getTime();
            switch (states) {
                case STATE_RW:
                    try {
                        if (((intersample_time - tau) > 0) ) {
                            pause(&pauseCount);
                            SampleTime += TIME_STEP;
                            
                            break;
                        }
                        robot.RandomWalk();
                        if(robot.state == 0){intersample_time+=TIME_STEP;}
                        if(robot.state == 3){intersample_time+=TIME_STEP;}
                        //if(robot.state == 3){intersample_time = 0;}
                        if(robot.state == 6){intersample_time = 0;}
                        if(robot.state == 7){intersample_time = 0;}
                        recvSample();

                    } catch (const std::exception &e) {
                        std::cerr << "Error in STATE_RW: " << e.what() << std::endl;
                        states = RESET;  // Transition to RESET state to handle the error
                    }
                    break;

                case STATE_OBS:
                    try {
                        pauseCount = 1000;
                        sample = environ.getSample(robot.getPos()[0], robot.getPos()[1]);
                        beta.update(sample);
                        beta.onboard_update(sample);
                        check_decision();
                        message = calculateMessage(sample);
                        print_data(1);
                        sendSample(message);
                        robot.battery_drain = (1 - robot.d_robot->getTime() /(TIME_MAX*7 ));//simulate a voltage drop
                        robot.setSpeedDistParams(3.1,0.095,0.8);//simulate random variations in speed due to surface, direction, friction etc.
                        states = STATE_RW;
                        intersample_time =0;
                    } catch (const std::exception &e) {
                        std::cerr << "Error in STATE_OBS: " << e.what() << std::endl;
                        states = RESET;  // Transition to RESET state to handle the error
                    }
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

            // Optionally, print additional data or debug information
            // print_data(0);

        }

        return;
        
}


void Algorithm1::print_data(int print_bool) {//0 for not printing and only in custom data, 1 for also printing.
if(robot.d_robot->getTime() > 5) {
    std::string customData = 
        std::to_string(print_bool) + "," +
        std::to_string((double) robot.d_robot->getTime()) + "," +
        std::string(robot.d_robot->getName().substr(1, 1)) + "," +
        std::to_string(environ.lastSample) + "," +
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
    std::cout << "Settings values for robot: "<<robot.d_robot->getName() << "---------------"<<"\n";
    for (int value : settings.values) {
        std::cout << value << " ";
    }
    std::cout << std::endl;

    robot.setSeeds(settings.values[7] + 1);

    std::string name = robot.d_robot->getName();
    int seed =((int) name[1] +1) * 1357 * (settings.values[7]+1);
    sf_rd.seed(seed);
    robot.setRWTimeGenParams(settings.values[0], settings.values[1]);
    robot.setAngleDistParams(-0.1,0.1);
    robot.setSpeedDistParams(3.1,0.095,0.8);

    environ.setSeed((settings.values[7]+1) * robot.SeedRov * 123);
    environ.d_nrTiles = settings.values[9];
    Us_exponent = ((double) settings.values[10]) / 1000;

    environ.setNonVibDistribution(2.52194,0.28754,0.13731 );
    environ.setVibDistribution(5.33497,0.5132,-0.2001);

    environ.setFPdist(settings.values[11]);
    environ.setFNdist(settings.values[12]);

    environ.method_read = settings.values[8];
    environ.vibThresh = 1.33; // corresponding to around 14% error margin


    tau = settings.values[2];
    robot.CA_Threshold = settings.values[3];
    min_swarmCount = settings.values[4];
    feedback = static_cast<feedbackStrategy>(settings.values[5]);
    eta = settings.values[6];
    // Print the updated values 
    std::cout << "tau: " << tau << std::endl;
    std::cout << "CA_Threshold: " << robot.CA_Threshold << std::endl;
    std::cout << "min_swarmCount: " << min_swarmCount << std::endl;
    std::cout << "feedback: " << feedback << std::endl;
    std::cout << "eta: " << eta << std::endl;
    std::cout << "End of settings values for robot: "<<robot.d_robot->getName() << "---------------"<<"\n";
}


void Algorithm1::pause(int *pause_Time) {
    // Stop the robot's movement
    robot.setSpeed(0, 0);
    
    // Check if pause time has elapsed, if yes, transition to observation state
    if (*pause_Time <= TIME_STEP) {
        states = STATE_OBS;
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
        // The above sometimes works even betteras the lower one, gives computational difference due to floating point operations.
        //delta = exp(-1.0*eta * beta.getVariance()) * (0.5-beta.getBelief()) * (0.5-beta.getBelief());


       
        delta = exp(-1.0 * eta * beta.getVariance()) * std::pow(std::abs(0.5 - beta.getBelief()), Us_exponent);
        soft_feedback.param(std::bernoulli_distribution::param_type( delta * (1.0 - beta.getBelief()) + (1-delta) * sample ));
        return soft_feedback(sf_rd);
    }
    else{ return sample;}//in exception cases

}


#endif // INCLUDED_ALGORITHM1_HH_














