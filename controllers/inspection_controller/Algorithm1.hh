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
#include "SHM.hh"
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

    Algorithm1() : settings(),robot(TIME_STEP),naturalFreq(2.0,2.0,100.0),radio(robot.d_robot,TIME_STEP) {};

    void run();
    void getSample(int posx, int posy);
    void detectPeaks(Array freqArray);
    void saveFilteredData(const std::vector<double>& data, const std::string& filename);
    void recvSample();
    void sendSample(int sample);

private:
    ControllerSettings settings;
    RugRobot robot;
    eigenFreq naturalFreq;
    Radio_Rover radio;
    std::vector<int> pos;

 
    double sample_freq = 200.0; //Sample rate in Hz
    double sample_length = 4.5; //Sample length in seconds
    double sample_pause = 0.0;
    double dt = 1/sample_freq; //Time between samples

    double cutoff_freq = 1.0;  // Cutoff frequency in Hz
    std::vector<double> b = { 0.04125354, 0.08250707, 0.04125354 };
    std::vector<double> a = {  1.      ,   -1.34896775 , 0.51398189 };

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
    //std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;
    pos = roundToNearest10(robot.getPos());
    robot.setCustomData("");
    settings.readSettings();

    for (int i = 0; i <= 1; ++i) {
        naturalFreq.a[i] = (double)settings.values[i];
    }
    for (int i = 0; i <= 1; ++i) {
        naturalFreq.b[i] = (double)settings.values[i+2];
    }
    naturalFreq.learning_rate = settings.values[4];
    naturalFreq.upper_freq = settings.values[5];
    
    CArray fft_results(N_samples); //complex array to store FFT results
    Array freqArray = createFrequencyArray(sample_freq, N_samples);

    

    while(robot.d_robot->step(TIME_STEP) != -1) {
        
        switch(states) {

            case STATE_RW:

                if(robot.RandomWalk()==1){
 
                    states = STATE_OBS;
                }
                if (naturalFreq.iteration>0)
                    {recvSample();}
                break;

            case STATE_OBS:
                sample_pause+=TIME_STEP;
                if (sample_pause < (sample_length * 1000)){
                    break;
                }
                sample_pause = 0.0;
                pos = roundToNearest10(robot.getPos());

                getSample(pos[0],pos[1]);
                for (size_t i = 0; i < numbers.size(); ++i) {
                    fft_results[i] = Complex(numbers[i], 0);
                }
                fft(fft_results);
                abs_fft_results = compute_abs_fft(fft_results);
                pos_abs_fft_results.assign(abs_fft_results.begin(), abs_fft_results.begin() + half_size);
                detectPeaks(freqArray);

                naturalFreq.update(naturalFreq.checkSample(peak_freq[0]));

                sendSample(naturalFreq.checkSample(peak_freq[0]));  
                
                states = STATE_RW;                  
                break;


            case STATE_PAUSE:
                // Pause logic here
                break;
        }
        if(robot.d_robot->getTime()>5){
        robot.setCustomData( std::to_string((int) robot.d_robot->getTime())+
        ","+std::string(robot.d_robot->getName().substr(1,1)) + 
        ","+std::to_string(naturalFreq.getEstimatedFreq()) +
        ","+std::to_string(robot.getPos()[0])+
        ","+std::to_string(robot.getPos()[1])+
        ","+std::to_string(naturalFreq.alpha)+
        ","+std::to_string(naturalFreq.beta)+
        "," + std::to_string(naturalFreq.iteration));
        
        }
    }
}


void Algorithm1::recvSample(){
    std::vector<int> messages = radio.getMessages();
        // Process received messages
        for (int sample : messages) {
            //std::cout <<"recv " << sample<<'\n';
            naturalFreq.update(sample);
        }
}

void Algorithm1::sendSample(int sample){

    // Determine the message to send based on decision flag or observation color
    int const *message;

    message = &sample;
    // Send the message
    radio.sendMessage(message, sizeof(message));

}

void Algorithm1::getSample(int posx, int posy) {
    
    // Construct the file path based on posx and posy
    std::filesystem::path currentPath = std::filesystem::current_path();
    // Assuming this code is located in the controllers/inspection_controller directory
    std::filesystem::path basePath = currentPath.parent_path().parent_path();
    std::string filePath = (basePath / "measurements" / ("acc_x" + std::to_string(posx) + "_y" + std::to_string(posy) + ".txt")).string();

    //std::cout << "Attempting to open file: " << filePath << std::endl; // Add this line for debugging

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
    //saveFilteredData(pos_abs_fft_results,"fft_output.txt");

    // Apply Butterworth filter in forward direction and get filtered output
    std::vector<double> filtered_fft_forward = forwardButterworth(b, a, pos_abs_fft_results);

    // Apply Butterworth filter in backward direction using forward filtered output for zero phase shift
    std::vector<double> filtered_fft_backward = backwardButterworth(b, a, filtered_fft_forward);

    filtered_fft = filtered_fft_backward;
    //saveFilteredData(filtered_fft,"fft_filtered.txt");

    // Detect peaks in the signal
    std::vector<int> index;
    for (int i = 1; i < filtered_fft.size() - 1; ++i) {
        if (filtered_fft[i-1] < filtered_fft[i] && filtered_fft[i+1] < filtered_fft[i]) {
            index.push_back(i);
        }
    }
    // Number of peaks wanted
    int N_peaks = 3;

    // Sort indices based on filtered_data values
    std::sort(index.begin(), index.end(), [&](int i1, int i2) {
        return filtered_fft[i1] > filtered_fft[i2];
    });
    // Get top N peaks (indices)
    std::vector<int> top_indices;
    const double min_distance = 0.1;  // Adjust this minimum distance as needed
    double last_freq = -1.0;
    for (int i = 0; i < N_peaks && i < index.size(); ++i) {
        int idx = index[i];
        double current_freq = freqArray[idx];

        // Check if the current peak is far enough from the last selected peak
        if (last_freq == -1.0 || std::abs(current_freq - last_freq) >= min_distance) {
            top_indices.push_back(idx);
            last_freq = current_freq;
        }
    }


    peak_mag.clear();
    peak_freq.clear();

    std::vector<std::pair<double, double>> peaks;
    for (const auto& idx : top_indices) {
        peaks.emplace_back( freqArray[idx],filtered_fft[idx]);
    }

    // Sort peaks based on frequency
    std::sort(peaks.begin(), peaks.end(), [](const std::pair<double, double>& a, const std::pair<double, double>& b) {
        return a.first < b.first;
    });

    // Extract sorted frequencies and magnitudes
    for (const auto& peak : peaks) {
        peak_mag.push_back(peak.second);
        peak_freq.push_back(peak.first);
        //std::cout << "Mag: " << peak.second << ", Frequency: " << peak.first << std::endl;
    }

    //appendValuesToFile(peak_freq, peak_mag);

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
