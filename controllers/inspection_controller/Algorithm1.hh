#ifndef INCLUDED_ALGORITHM1_HH_
#define INCLUDED_ALGORITHM1_HH_
#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <vector>
#include <cmath>
#include <filesystem>
#include "filtering.hh"


#include "RugBot.hh"



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
    RugRobot robot;
    // Time step for the simulation
    enum { TIME_STEP = 20 };
    


    Algorithm1() : robot(TIME_STEP){};
    void run();
    void getSample(int posx, int posy);
    void detectPeaks(Array freqArray);
    void saveFilteredData(const std::vector<double>& data, const std::string& filename);
private:
    std::vector<int> pos;

    double sample_freq = 200.0; //Sample rate in Hz
    double sample_length = 4.5; //Sample length in seconds
    double dt = 1/sample_freq; //Time between samples

    double cutoff_freq = 15.0;  // Cutoff frequency in Hz

    int N_samples = ((sample_freq) * sample_length);
    int half_size = N_samples / 2 + 1;

    std::vector<double> numbers;
    std::vector<double> abs_fft_results;
    std::vector<double> filtered_fft;
    std::vector<double> pos_abs_fft_results;
    std::vector<double> peak_freq;
    std::vector<double> peak_mag;
};


void Algorithm1::run() {
    std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;
    

    CArray fft_results(N_samples); //complex array to store FFT results
    Array freqArray = createFrequencyArray(sample_freq, N_samples);



    while(robot.d_robot->step(TIME_STEP) != -1) {
        
        switch(states) {
            case STATE_RW:

                if(robot.RandomWalk()==1){
                    std::cout<<"random walk done" <<'\n';
                    states = STATE_OBS;
                }
                
                break;

            case STATE_OBS:
                pos = roundToNearest10(robot.getPos());
                getSample(pos[0],pos[1]);
                for (size_t i = 0; i < numbers.size(); ++i) {
                    fft_results[i] = Complex(numbers[i], 0);
                }
                fft(fft_results);
                abs_fft_results = compute_abs_fft(fft_results);

                pos_abs_fft_results.assign(abs_fft_results.begin(), abs_fft_results.begin() + half_size);

                detectPeaks(freqArray);
                states = STATE_RW;


                        
                break;

            case STATE_PAUSE:
                // Pause logic here
                break;
        }
    }
}

void Algorithm1::getSample(int posx, int posy) {
    // Construct the file path based on posx and posy
    std::string filePath = "/home/thiemenrug/Documents/GitHub/RugBotSim/measurements/acc_x" + std::to_string(posx) + "_y" + std::to_string(posy) + ".txt";
    std::cout << "Attempting to open file: " << filePath << std::endl; // Add this line for debugging

    // Open the file
    std::ifstream inputFile(filePath);
    if (!inputFile.is_open()) {
        std::cerr << "Failed to open file: " << filePath << std::endl;
        return;
    }

    // Clear the vector to avoid appending to old data
    numbers.clear();
    double number;

    // Read up to N_samples lines from the file
    for (int i = 0; i < N_samples; i++) {
        std::string line;
        if (std::getline(inputFile, line)) {
            // Convert the line to a double and add it to the vector
            number = std::stod(line);

            numbers.push_back(number);
        } else {
            break; // Stop reading if fewer than 5 lines are available
        }
        states= STATE_PAUSE;
    }
}
void Algorithm1::detectPeaks(Array freqArray){
    saveFilteredData(pos_abs_fft_results,"fft_output.txt");
    filtered_fft = butter_lowpass_filter(pos_abs_fft_results, cutoff_freq, sample_freq);
    saveFilteredData(filtered_fft,"fft_filtered.txt");
    // Example peak detection and sorting (replace with your actual implementation)
    std::vector<int> index;
    for (int i = 1; i < filtered_fft.size() - 1; ++i) {
        if (filtered_fft[i-1] < filtered_fft[i] && filtered_fft[i+1] < filtered_fft[i]) {
            index.push_back(i);
        }
    }
    // Constants
    int N_peaks = 3;

    // Sort indices based on filtered_data values
    std::sort(index.begin(), index.end(), [&](int i1, int i2) {
        return filtered_fft[i1] > filtered_fft[i2];
    });
        // Get top N peaks (indices in this case)
    std::vector<int> top_indices;
    for (int i = 0; i < N_peaks && i < index.size(); ++i) {
        top_indices.push_back(index[i]);
    }
    // peak_mag.clear();
    // peak_freq.clear();
    // for (const auto& idx : top_indices) {
    //     peak_freq.push_back(freqArray[idx]);
    //     peak_mag.push_back(filtered_fft[idx]);
    //     std::cout << "Mag: " << filtered_fft[idx] << ", Frequency: " << freqArray[idx]  << std::endl;
    // }


}

void Algorithm1::saveFilteredData(const std::vector<double>& data, const std::string& filename) {
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
#endif // INCLUDED_ALGORITHM1_HH_














