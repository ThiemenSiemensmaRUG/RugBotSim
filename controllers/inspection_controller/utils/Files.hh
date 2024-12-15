#ifndef FILES_HH
#define FILES_HH

#include <fstream>
#include <iostream>
#include <vector>

/**
 * @brief Saves the filtered data to a specified file.
 *
 * This function takes a vector of doubles and writes each value to a new line
 * in the specified file.
 *
 * @param data A vector of double values to be saved.
 * @param filename The name of the file where the data will be saved.
 */
void saveFilteredData(const std::vector<double>& data, const std::string& filename) {
    std::ofstream outputFile(filename);
    if (!outputFile.is_open()) {
        std::cerr << "Failed to open file for writing: " << filename << std::endl;
        return;
    }

    for (const auto& value : data) {
        outputFile << value << "\n";
    }

    outputFile.close();
}

/**
 * @brief Appends the peak frequencies and magnitudes to a specified file.
 *
 * This function takes two vectors of doubles and appends the values to a file.
 *
 * @param peak_freq A vector of peak frequencies.
 * @param peak_mag A vector of peak magnitudes.
 */
void appendValuesToFile(const std::vector<double>& peak_freq, const std::vector<double>& peak_mag) {
    std::ofstream outFile("freq_mag_output.txt", std::ios::app);  // Open file for appending

    if (!outFile) {
        std::cerr << "Failed to open output.txt for appending!" << std::endl;
        return;
    }

    for (size_t i = 0; i < peak_freq.size(); ++i) {
        outFile << peak_freq[i] << ",";
    }
    outFile << std::endl;

    outFile.close();
}

#endif  // FILES_HH