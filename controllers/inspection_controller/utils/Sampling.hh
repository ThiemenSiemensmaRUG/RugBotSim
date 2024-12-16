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
    std::string filePath = (basePath / "measurements" / "jobs" / "damaged" / "modal_shape_damaged.csv").string();

    std::ifstream inputFile(filePath);
    if (!inputFile.is_open()) {
        std::cerr << "Failed to open file: " << filePath << std::endl;
        return {};
    }

    // Skip the header line
    std::string header;
    std::getline(inputFile, header);

    struct Point {
        double x, y, u3, mode_num;
        double distance(int px, int py) const {
            return std::sqrt(std::pow(x - px, 2) + std::pow(y - py, 2));
        }
    };

    std::vector<Point> points;
    
    std::string line;
    while (std::getline(inputFile, line)) {
        std::stringstream ss(line);
        std::string token;
        std::vector<double> values;

        while (std::getline(ss, token, ',')) {
            try {
                values.push_back(std::stod(token));
            } catch (const std::exception& e) {
                std::cerr << "Error converting token to double: " << e.what() << std::endl;
            }
        }

        if (values.size() >= 8) {
            points.push_back({values[1], values[2], values[7], values[4]});
        }
    }

    if (points.empty()) {
        std::cerr << "No points found in file: " << filePath << std::endl;
        return {};
    }

    Point closestPoint = points[0];
    double closestDistance = closestPoint.distance(posx, posy);

    for (const auto& point : points) {
        double distance = point.distance(posx, posy);
        if (distance < closestDistance) {
            closestPoint = point;
            closestDistance = distance;
        }
    }

    std::vector<double> numbers;
    
    return {closestPoint.u3, closestPoint.mode_num, closestPoint.x, closestPoint.y};
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