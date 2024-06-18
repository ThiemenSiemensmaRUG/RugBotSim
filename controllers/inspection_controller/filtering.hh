
#include <complex>
#include <vector>
#include <cmath>


const double PI = 3.141592653589793238460;


typedef std::complex<double> Complex;
typedef std::vector<Complex> CArray;
typedef std::vector<double> Array;


// Cooley-Tukey FFT (in-place, breadth-first, decimation-in-frequency)
void fft(CArray& x) {
    const size_t N = x.size();
    if (N <= 1) return;
    // divide
    CArray even = CArray(N / 2);
    CArray odd = CArray(N / 2);
    for (size_t i = 0; i < N / 2; ++i) {
        even[i] = x[i*2];
        odd[i] = x[i*2 + 1];
    }
    // conquer
    fft(even);
    fft(odd);
    // combine
    for (size_t k = 0; k < N / 2; ++k) {
        Complex t = std::polar(1.0, -2.0 * PI * k / N) * odd[k];
        x[k] = even[k] + t;
        x[k + N / 2] = even[k] - t;
    }
}

Array createFrequencyArray(double sample_freq, int N_samples) {
    int half_size = N_samples / 2 + 1;
    Array freqArray(half_size);
    double freq_step = sample_freq / N_samples;
    for (int i = 0; i < half_size; ++i) {
        freqArray[i] = i * freq_step;
    }
    return freqArray;
}

// Function to perform a first-order Butterworth lowpass filter on absolute values
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

// Function to compute absolute values of FFT results (magnitude)
std::vector<double> compute_abs_fft(const std::vector<std::complex<double>>& fft_results) {
    std::vector<double> abs_fft_results(fft_results.size());

    for (size_t i = 0; i < fft_results.size(); ++i) {
        abs_fft_results[i] = std::abs(fft_results[i]); // Compute magnitude of complex number
    }

    return abs_fft_results;
}


std::vector<int> roundToNearest10(const std::vector<int>& numbers) {
    std::vector<int> rounded_numbers;
    rounded_numbers.reserve(numbers.size());

    for (int number : numbers) {
        // Calculate the remainder when divided by 10
        int remainder = number % 10;

        // Determine the nearest multiple of 10
        int nearest;
        if (remainder < 5) {
            nearest = number - remainder;
        } else {
            nearest = number + (10 - remainder);
        }

        // Store the rounded number
        rounded_numbers.push_back(nearest);
    }

    return rounded_numbers;
}