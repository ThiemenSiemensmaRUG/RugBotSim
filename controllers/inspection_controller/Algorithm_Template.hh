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

    Algorithm1() : settings(), robot(TIME_STEP), environ("world.txt"), radio(robot.d_robot, TIME_STEP) {};

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

    void readDataFromFile(const std::string& filename);
};

void Algorithm1::run() {
    std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;

    robot.setCustomData("");
    settings.readSettings();

    while (robot.d_robot->step(TIME_STEP) != -1) {
        switch (states) {
            case STATE_RW:
                if (robot.RandomWalk() == 1) {
                    states = STATE_OBS;
                }
                break;

            case STATE_OBS:
                sample_ = environ.getSample(robot.getPos()[0], robot.getPos()[1]);
                std::cout << "Sample: " << sample_ << " Robot position: " 
                          << 1.0 * robot.getPos()[0] / 100 << " " << 1.0 * robot.getPos()[1] / 100 << "\n";

                if (sample_ == 0) {
                    // Read data from file
                    readDataFromFile("../../data/capture1_60hz_30vol.txt");  
                }

                states = STATE_RW;
                break;

            case STATE_PAUSE:
                // Pause logic here
                break;
        }
        
        if (robot.d_robot->getTime() > 5) {
            robot.setCustomData(std::to_string((int)robot.d_robot->getTime()) +
                "," + std::string(robot.d_robot->getName().substr(1, 1)));
        }
    }
}

void Algorithm1::readDataFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return;
    }

    std::string line;
    while (std::getline(file, line)) {
        // Process each line here as needed
        std::cout << "Read line: " << line << std::endl;

        // Example: parse line data (if numeric data is stored in lines)
        // double data = std::stod(line); // If you need to convert line to a number
    }
    file.close();
}

void Algorithm1::recvSample() {
    std::vector<int> messages = radio.getMessages();
    for (int sample : messages) {
        // Process received messages
    }
}

void Algorithm1::sendSample(int sample) {
    int const *message;
    message = &sample;
    radio.sendMessage(message, sizeof(message));
}

#endif // INCLUDED_ALGORITHM1_HH_
