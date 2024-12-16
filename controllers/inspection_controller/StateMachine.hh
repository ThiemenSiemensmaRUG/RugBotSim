#ifndef INCLUDED_STATEMACHINE_HH_
#define INCLUDED_STATEMACHINE_HH_
#include <cmath>
#include <complex>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>

#include "RugBot.hh"
#include "SHM.hh"
#include "controller_settings.hh"
#include "filtering.hh"
#include "radio.hh"
#include "utils/Sampling.hh"

typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;

#define ACCURACY 10

class StateMachine {
   public:
    enum AlgoStates {
        STATE_RW,    // State: Random Walk
        STATE_OBS,   // State: Observe Color
        STATE_PAUSE  // etc....
    };

    AlgoStates states = STATE_RW;

    // Time step for the simulation
    enum { TIME_STEP = 20 };

    StateMachine()
        : settings(),
          robot(TIME_STEP),
          naturalFreq(2.0, 2.0, 100.0),
          radio(robot.d_robot, TIME_STEP) {};
    void run();

   private:
    ControllerSettings settings;
    RugRobot robot;
    eigenFreq naturalFreq;
    Radio_Rover radio;
    std::vector<int> pos;

    double sample_freq = 200.0;  // Sample rate in Hz
    double sample_length = 4.5;  // Sample length in seconds
    double sample_pause = 0.0;
    double dt = 1.0 / sample_freq;  // Time between samples

    double cutoff_freq = 1.0;  // Cutoff frequency in Hz
    std::vector<double> b = {0.04125354, 0.08250707, 0.04125354};
    std::vector<double> a = {1., -1.34896775, 0.51398189};

    int N_samples = ((sample_freq)*sample_length);
    int half_size = N_samples / 2 + 1;

    std::vector<double> numbers;
    std::vector<double> abs_fft_results;
    std::vector<double> filtered_fft;
    std::vector<double> pos_abs_fft_results;
    std::vector<double> peak_freq;
    std::vector<double> peak_mag;

    Sampling sampler;
};

/**
 * @brief Executes the main algorithm loop for the robot's inspection controller.
 *
 * This function performs the following steps:
 * 1. Initializes the robot's position and settings.
 * 2. Reads settings and initializes natural frequency parameters.
 * 3. Creates an array to store FFT results and a frequency array.
 * 4. Enters a loop that continues while the robot is active.
 * 5. Depending on the current state, performs actions such as random walk, obstacle detection,
 *    sampling, FFT computation, peak detection, and frequency update.
 * 6. Sends the sample data and updates the robot's custom data with the current state and frequency information.
 *
 * The function handles three states:
 * - STATE_RW: Random walk state where the robot moves randomly for a certain time period.
 * - STATE_OBS: Obstacle state where the robot pauses, samples data, performs FFT, detects peaks,
 *              updates natural frequency, and sends the sample.
 * - STATE_PAUSE: Pause state where the robot is stationary.
 *
 * The function also outputs the robot's time, name, estimated frequency, position, alpha, beta, and iteration count.
 */
void StateMachine::run() {
    pos = roundToNearestX(robot.getPos(), ACCURACY);
    robot.setCustomData("");
    settings.readSettings();

    for (int i = 0; i <= 1; ++i) {
        naturalFreq.a[i] = (double)settings.values[i];
    }
    for (int i = 0; i <= 1; ++i) {
        naturalFreq.b[i] = (double)settings.values[i + 2];
    }
    naturalFreq.learning_rate = settings.values[4];
    naturalFreq.upper_freq = settings.values[5];

    CArray fft_results(N_samples);  // complex array to store FFT results
    Array freqArray = createFrequencyArray(sample_freq, N_samples);

    while (robot.d_robot->step(TIME_STEP) != -1) {
        switch (states) {
            case STATE_RW: {
                if (robot.RandomWalk() == 1) {
                    states = STATE_OBS;
                }
                if (naturalFreq.iteration > 0) {
                    sampler.recvSample(naturalFreq, radio);
                }
                break;
            }

            case STATE_OBS: {
                sample_pause += TIME_STEP;
                if (sample_pause < (sample_length * 1000)) {
                    break;
                }
                sample_pause = 0.0;
                pos = roundToNearestX(robot.getPos(), ACCURACY);

                auto numbers = sampler.getSample(pos[0], pos[1], N_samples);
                for (size_t i = 0; i < numbers.size(); ++i) {
                    fft_results[i] = Complex(numbers[i], 0);
                }
                fft(fft_results);
                abs_fft_results = compute_abs_fft(fft_results);
                pos_abs_fft_results.assign(abs_fft_results.begin(), abs_fft_results.begin() + half_size);
                detectPeaks(freqArray, filtered_fft, peak_freq, peak_mag, b, a, pos_abs_fft_results);

                naturalFreq.update(naturalFreq.checkSample(peak_freq[0]));

                sampler.sendSample(naturalFreq.checkSample(peak_freq[0]), radio);

                states = STATE_RW;
                break;
            }

            case STATE_PAUSE:
                break;
        }
        if (robot.d_robot->getTime() > 5 && samples.size() > 0) {
            robot.setCustomData(std::to_string((int)robot.d_robot->getTime()) +
                                "," + std::string(robot.d_robot->getName().substr(1)) +
                                "," + std::to_string(naturalFreq.getEstimatedFreq()) +
                                "," + std::to_string(robot.getPos()[0]) +
                                "," + std::to_string(robot.getPos()[1]) +
                                "," + std::to_string(naturalFreq.alpha) +
                                "," + std::to_string(naturalFreq.beta) +
                                "," + std::to_string(naturalFreq.iteration));
        }
    }
}

#endif  // INCLUDED_STATEMACHINE_HH_
