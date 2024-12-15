#ifndef INCLUDED_SAMPLING_HH_
#define INCLUDED_SAMPLING_HH_

#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

#include "radio.hh"

class Sampling {
   public:
    Sampling() {};
    std::vector<double> getSample(int posx, int posy, int N_samples);
    void recvSample(eigenFreq& naturalFreq, Radio_Rover& radio);
    void sendSample(int sample, Radio_Rover& radio);
};

/**
 * @brief Reads a sample of data from a file, based on the given position coordinates.
 *
 * This function first constructs the file path based on the x and y coordinates,
 * and attempts to open the corresponding file located in the "measurements" directory.
 * It reads up to N_samples lines from the file, converts each line to a double, then stores
 * the values in the `numbers` vector.
 *
 * @param posx The x-coordinate used to construct the file name.
 * @param posy The y-coordinate used to construct the file name.
 * @param N_samples The number of samples to read from the file.
 */
std::vector<double> Sampling::getSample(int posx, int posy, int N_samples) {
    std::filesystem::path currentPath = std::filesystem::current_path();
    // Assuming this code is located in the controllers/inspection_controller directory
    std::filesystem::path basePath = currentPath.parent_path().parent_path();
    std::string filePath = (basePath / "measurements" / ("acc_x" + std::to_string(posx) + "_y" + std::to_string(posy) + ".txt")).string();

    std::ifstream inputFile(filePath);
    if (!inputFile.is_open()) {
        std::cerr << "Failed to open file: " << filePath << std::endl;
        return {};
    }

    double number;
    std::vector<double> numbers;
    for (int i = 0; i < N_samples; i++) {
        std::string line;
        if (std::getline(inputFile, line)) {
            // Convert to a double and add it to the vector
            number = std::stod(line);
            numbers.push_back(number);
        } else {
            break;
        }
    }

    return numbers;
}

/**
 * @brief Receives and processes samples from the radio.
 *
 * This function retrieves a list of messages from the radio and processes each
 * message by updating the natural frequency with the received sample.
 */
void Sampling::recvSample(eigenFreq& naturalFreq, Radio_Rover& radio) {
    std::vector<int> messages = radio.getMessages();
    for (int sample : messages) {
        naturalFreq.update(sample);
    }
}

/**
 * @brief Sends a sample value as a message.
 *
 * This function takes an integer sample value, determines the message
 * to send based on the decision flag or observation color, and sends the message.
 *
 * @param sample The flag or observation color to send as a message.
 */
void Sampling::sendSample(int sample, Radio_Rover& radio) {
    int const message = sample;
    radio.sendMessage(&message, sizeof(int));
}

#endif  // INCLUDED_SAMPLING_HH_