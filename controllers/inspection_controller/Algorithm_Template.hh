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

    // Hardcoded input data
    std::vector<double> inputData = {
        0.46838379, 0.48919678, 0.74868774,
        0.46890259, 0.48904419, 0.74890137,
        0.46881104, 0.48913574, 0.74896240,
        0.46868896, 0.48947144, 0.74896240,
        0.46847534, 0.48898315, 0.74911499,
        0.46856689, 0.48928833, 0.74868774,
        0.46844482, 0.48916626, 0.74914551,
        0.46856689, 0.48892212, 0.74865723,
        0.46859741, 0.48889160, 0.74877930,
        0.46844482, 0.48876953, 0.74868774,
        0.46817017, 0.48883057, 0.74899292,
        0.46862793, 0.48928833, 0.74832153,
        0.46859741, 0.48919678, 0.74905396,
        0.46829224, 0.48922729, 0.74893188,
        0.46856689, 0.48913574, 0.74911499,
        0.46871948, 0.48907471, 0.74914551,
        0.46856689, 0.48934937, 0.74923706,
        0.46841431, 0.48889160, 0.74838257,
        0.46908569, 0.48895264, 0.74920654,
        0.46878052, 0.48959351, 0.74926758,
        0.46817017, 0.48889160, 0.74880981,
        0.46929932, 0.48919678, 0.74896240,
        0.46859741, 0.48925781, 0.74908447,
        0.46911621, 0.48873901, 0.74853516
    };

    // Write input data to a temporary file
    std::ofstream outfile("input_data.txt");
    for (const double& val : inputData) {
        outfile << val << " ";
    }
    outfile.close();

    // Run keras2cpp executable with input file and capture the output
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen("./keras2cpp input_data.txt", "r"), pclose);
    if (!pipe) {
        std::cerr << "Error: popen() failed" << std::endl;
        return;
    }

    // Read the output of keras2cpp line by line
    char buffer[128];
    std::string output;
    while (fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
        output += buffer;
    }

    // Restore the original working directory
    chdir(originalDir);

    // Print the captured output
    std::cout << "keras2cpp output: " << output << std::endl;
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
                    std::ofstream file("../../data/curr_data.txt", std::ofstream::trunc);  

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
                } 

                // Call the keras2cpp executable and capture its output
                runKeras2cppExecutable();

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
