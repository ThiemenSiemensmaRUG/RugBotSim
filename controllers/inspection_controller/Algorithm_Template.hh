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

#include <unistd.h> // for chdir
#include <cstdio>
#include <memory>
#include <thread>
#include <chrono>
#include <string>
#include <algorithm>

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
    void runKeras2cppExecutable();

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

void Algorithm1::runKeras2cppExecutable() {
    // Save the current working directory
    char originalDir[256];
    getcwd(originalDir, sizeof(originalDir));

    // Change to the keras2cpp/build directory
    chdir("../keras2cpp/build");

    // Run keras2cpp with the dynamically generated data file as input
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen("./keras2cpp curr_data.txt", "r"), pclose);
    if (!pipe) {
        std::cerr << "Error: popen() failed" << std::endl;
        return;
    }

    // Capture the output from keras2cpp line by line
    char buffer[128];
    std::string output;
    while (fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
        output += buffer;
    }

    // Restore the original working directory
    chdir(originalDir);

    // Remove square brackets and replace commas with spaces
    output.erase(std::remove_if(output.begin(), output.end(),
                                [](char c) { return c == '[' || c == ']'; }),
                 output.end());
    std::replace(output.begin(), output.end(), ',', ' ');

    // Print the cleaned output
    std::cout << "Cleaned keras2cpp output: " << output << std::endl;

    // Parse output to find the index with the highest value
    std::istringstream iss(output);
    std::vector<double> values;
    double number;
    while (iss >> number) {
        values.push_back(number);
    }

    // Find the index of the maximum value
    if (!values.empty()) {
        auto max_it = std::max_element(values.begin(), values.end());
        int max_index = std::distance(values.begin(), max_it);
        std::cout << "Index of the highest value: " << max_index << std::endl;
        std::cout << "Highest value: " << *max_it << std::endl;
    } else {
        std::cout << "No values found in the output." << std::endl;
    }
}


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
                    // Writing current data in a file to be read for inference
                    std::ofstream file("../keras2cpp/build/curr_data.txt", std::ofstream::trunc);  

                    if (!file.is_open()) {
                        std::cerr << "Error: Unable to open file " << std::endl;
                        return;
                    }

                    for (const auto& row : data_matrix) {
                        for (size_t i = 0; i < row.size(); ++i) {
                            file << row[i];
                            if (i < row.size() - 1) file << "\t";  
                        }
                        file << "\n";  
                    }
                    
                    file.close();
                    //std::this_thread::sleep_for(std::chrono::milliseconds(100));  // Wait for 100 ms
                    // Call the keras2cpp executable and capture its output
                    runKeras2cppExecutable();
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
