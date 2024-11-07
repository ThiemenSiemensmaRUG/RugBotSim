#ifndef INCLUDED_ALGORITHM1_HH_
#define INCLUDED_ALGORITHM1_HH_
#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <cmath>
#include <utility>
#include <filesystem>
#include <sstream>

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
    std::vector<std::vector<double>> data_matrix; // Matrix to store file data
    std::vector<std::vector<double>> readDataFromFile(const std::string& filename);
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

                if (static_cast<int>(robot.d_robot->getTime()) > 25){ 
                    if (sample_ == 0) {
                        // Read data from file and capture the returned matrix
                        data_matrix = readDataFromFile("../../data/capture1_60hz_30vol.txt");  

                    } else {
                        if (sample_ == 1) {
                            data_matrix = readDataFromFile("../../data/capture2_40hz_60vol.txt"); 
                        } else {
                            std::cout << "Not a black or white tile." << "\n";
                            data_matrix = std::vector<std::vector<double>>(24, std::vector<double>(3, 0.0));
                        }
                    }
                    // std::cout << "Data Matrix: " << std::endl;
                    // for (const auto& row : data_matrix) {
                    //     for (const auto& val : row) {
                    //         std::cout << val << "\t";
                    //     }
                    //     std::cout << std::endl;
                    // }
                    // std::cout << "TIMESTAMP " << robot.d_robot->getTime() << "\n";
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


std::vector<std::vector<double>> Algorithm1::readDataFromFile(const std::string& filename) {
    std::ifstream file(filename);
    std::vector<std::vector<double>> data_matrix;

    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return data_matrix; // Return an empty matrix if file cannot be opened
    }

    // Get the current timestamp as the starting row number
    int start_row = static_cast<int>(robot.d_robot->getTime()) - 24;
    
    std::string line;
    int current_row = 0;
    while (std::getline(file, line)) {
        // If the current row is less than the start row, skip it
        if (current_row < start_row) {
            ++current_row;
            continue;
        }

        // Stop reading if we have read 24 rows
        if (data_matrix.size() >= 24) {
            break;
        }

        // Parse the line into doubles and store it in the matrix
        std::istringstream iss(line);
        std::vector<double> row;
        double value;
        while (iss >> value) {
            row.push_back(value);
        }

        if (!row.empty()) {
            data_matrix.push_back(row); // Add the row to the matrix
        }

        ++current_row;
    }

    file.close();

    return data_matrix; // Return the matrix
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
