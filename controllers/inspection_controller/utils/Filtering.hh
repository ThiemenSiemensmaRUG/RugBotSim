#ifndef FILTERING_HH
#define FILTERING_HH

#include <cmath>
#include <complex>
#include <vector>

#include "utils/Files.hh"

typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;

/**
 * @brief Fast Fourier Transform
 *
 * Computes the FFT of the given complex array in-place, using the Cooley-Tukey algorithm.
 *
 * @param x Complex array of input values
 */
void fft(CArray& x) {
    const size_t N = x.size();
    if (N <= 1) return;
    // divide
    CArray even = CArray(N / 2);
    CArray odd = CArray(N / 2);
    for (size_t i = 0; i < N / 2; ++i) {
        even[i] = x[i * 2];
        odd[i] = x[i * 2 + 1];
    }
    // conquer
    fft(even);
    fft(odd);
    // combine
    for (size_t k = 0; k < N / 2; ++k) {
        Complex t = std::polar(1.0, -2.0 * M_PI * k / N) * odd[k];
        x[k] = even[k] + t;
        x[k + N / 2] = even[k] - t;
    }
}

/**
 * @brief Create a Frequency Array object
 *
 * @param sample_freq Sample frequency
 * @param N_samples Number of samples
 * @return Array Frequency array
 */
Array createFrequencyArray(double sample_freq, int N_samples) {
    int half_size = N_samples / 2 + 1;
    Array freqArray(half_size);
    double freq_step = sample_freq / N_samples;
    for (int i = 0; i < half_size; ++i) {
        freqArray[i] = i * freq_step;
    }
    return freqArray;
}

/**
 * @brief Applies a first-order Butterworth lowpass filter to the given data.
 *
 * @param data Absolute values of the FFT results.
 * @param cutoff_freq
 * @param sampling_freq
 * @return std::vector<double> Filtered data.
 */
std::vector<double> butter_lowpass_filter(const std::vector<double>& data, double cutoff_freq, double sampling_freq) {
    std::vector<double> filtered_data(data.size());

    // Calculate filter parameters
    double RC = 1.0 / (cutoff_freq * 2 * M_PI);
    double dt = 1.0 / sampling_freq;
    double alpha = dt / (RC + dt);

    // Apply first-order lowpass filter
    filtered_data[0] = data[0];
    for (size_t i = 1; i < data.size(); ++i) {
        filtered_data[i] = alpha * data[i] + (1 - alpha) * filtered_data[i - 1];
    }

    return filtered_data;
}

/**
 * @brief Applies a Butterworth filter in the forward direction to the given FFT results.
 *
 * @param b The numerator coefficients of the Butterworth filter.
 * @param a The denominator coefficients of the Butterworth filter.
 * @param fft Vector of FFT results.
 * @return std::vector<double> Filtered FFT results.
 */
std::vector<double> forwardButterworth(const std::vector<double>& b, const std::vector<double>& a, const std::vector<double>& fft) {
    int len_fft = fft.size();
    int len_b = b.size();

    std::vector<double> filtered_fft(len_fft, 0.0);

    // Apply filter from len_b to len_fft-1 (forward direction)
    for (int i = len_b; i < len_fft; ++i) {
        filtered_fft[i] = b[0] * fft[i];
        for (int j = 1; j < len_b; ++j) {
            filtered_fft[i] += b[j] * fft[i - j];
            filtered_fft[i] -= a[j] * filtered_fft[i - j];
        }
    }

    return filtered_fft;
}

/**
 * @brief Applies a Butterworth filter in the backward direction to the given FFT results.
 *
 * @param b The numerator coefficients of the Butterworth filter.
 * @param a The denominator coefficients of the Butterworth filter.
 * @param fft_out The input array of FFT results.
 * @return A vector of double values representing the filtered FFT results.
 */
std::vector<double> backwardButterworth(const std::vector<double>& b, const std::vector<double>& a, const std::vector<double>& fft_out) {
    int len_fft = fft_out.size();
    int len_b = b.size();

    std::vector<double> filtered_fft(len_fft, 0.0);

    // Apply filter from len_fft-2 to 0 (backward direction)
    for (int i = len_fft - 2; i >= 0; --i) {
        filtered_fft[i] = b[0] * fft_out[i];
        for (int j = 1; j < len_b; ++j) {
            filtered_fft[i] += b[j] * fft_out[i + j];
            filtered_fft[i] -= a[j] * filtered_fft[i + j];
        }
    }

    return filtered_fft;
}

/**
 * @brief Computes the absolute values of the given FFT results. (Magnitude)
 *
 * @param fft_results The input array of complex numbers representing the FFT results.
 * @return A vector of double values representing the absolute values of the FFT results.
 */
std::vector<double> compute_abs_fft(const std::vector<std::complex<double>>& fft_results) {
    std::vector<double> abs_fft_results(fft_results.size());

    for (size_t i = 0; i < fft_results.size(); ++i) {
        abs_fft_results[i] = std::abs(fft_results[i]);  // Compute magnitude of complex number
    }

    return abs_fft_results;
}

/**
 * @brief Rounds the given numbers to the nearest multiple of x.
 *
 * @param numbers The input vector of numbers to be rounded.
 * @param x The value to which the numbers will be rounded.
 */
std::vector<int> roundToNearestX(const std::vector<int>& numbers, int x) {
    std::vector<int> rounded_numbers;
    rounded_numbers.reserve(numbers.size());

    for (int number : numbers) {
        int remainder = number % x;

        // Determine the nearest multiple of x
        int nearest;
        if (remainder < x / 2) {
            nearest = number - remainder;
        } else {
            nearest = number + (x - remainder);
        }

        rounded_numbers.push_back(nearest);
    }

    return rounded_numbers;
}

/**
 * @brief Detects peaks in the given frequency array after applying a Butterworth filter.
 *
 * Applies a Butterworth filter to the input frequency array in both forward and backward directions to achieve zero phase shift.
 * Detects peaks in the filtered signal and selects the top N peaks based on their magnitudes.
 * The selected peaks are sorted by frequency and stored in the variables `peak_freq` and `peak_mag`.
 * Uncomment the `saveFilteredData` and `appendValuesToFile` functions for debugging purposes.
 *
 * @param freqArray The input array of frequencies to be analyzed.
 * @param filtered_fft The output array of filtered FFT values.
 * @param peak_freq The output array of peak frequencies.
 * @param peak_mag The output array of peak magnitudes.
 * @param b The numerator coefficients of the Butterworth filter.
 * @param a The denominator coefficients of the Butterworth filter.
 * @param pos_abs_fft_results The input array of absolute FFT values.
 */
void detectPeaks(Array freqArray, std::vector<double>& filtered_fft, std::vector<double>& peak_freq, std::vector<double>& peak_mag, const std::vector<double>& b, const std::vector<double>& a, const std::vector<double>& pos_abs_fft_results) {
    // saveFilteredData(pos_abs_fft_results,"fft_output.txt");

    // Apply Butterworth filter in forward direction and get filtered output
    std::vector<double> filtered_fft_forward = forwardButterworth(b, a, pos_abs_fft_results);

    // Apply Butterworth filter in backward direction using forward filtered output for zero phase shift
    std::vector<double> filtered_fft_backward = backwardButterworth(b, a, filtered_fft_forward);

    filtered_fft = filtered_fft_backward;
    // saveFilteredData(filtered_fft,"fft_filtered.txt");

    // Detect peaks in the signal
    std::vector<int> index;
    for (std::vector<double>::size_type i = 1; i < filtered_fft.size() - 1; ++i) {
        if (filtered_fft[i - 1] < filtered_fft[i] && filtered_fft[i + 1] < filtered_fft[i]) {
            index.push_back(i);
        }
    }

    // Number of peaks wanted
    std::vector<int>::size_type N_peaks = 3;

    // Sort indices based on filtered_data values
    std::sort(index.begin(), index.end(), [&](int i1, int i2) {
        return filtered_fft[i1] > filtered_fft[i2];
    });

    // Get top N peaks (indices)
    std::vector<int> top_indices;
    const double min_distance = 0.1;  // Minimum distance between peaks to be considered separate peaks
    double last_freq = -1.0;
    for (std::vector<int>::size_type i = 0; i < N_peaks && i < index.size(); ++i) {
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
        peaks.emplace_back(freqArray[idx], filtered_fft[idx]);
    }

    // Sort peaks based on frequency
    std::sort(peaks.begin(), peaks.end(), [](const std::pair<double, double>& a, const std::pair<double, double>& b) {
        return a.first < b.first;
    });

    // Extract sorted frequencies and magnitudes
    for (const auto& peak : peaks) {
        peak_mag.push_back(peak.second);
        peak_freq.push_back(peak.first);
        // std::cout << "Mag: " << peak.second << ", Frequency: " << peak.first << std::endl;
    }

    // appendValuesToFile(peak_freq, peak_mag);
}

#endif  // FILTERING_HH