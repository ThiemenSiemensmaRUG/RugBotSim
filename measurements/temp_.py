import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter,filtfilt
import numpy as np
from scipy.signal import butter, freqz
import matplotlib.pyplot as plt

# Define the parameters for the Butterworth filter
order = 2  # Filter order
fs = 200.0  # Sample rate, Hz
cutoff_freq = 15.0  # Desired cutoff frequency of the filter, Hz

# Normalize the cutoff frequency
normalized_cutoff = cutoff_freq / (fs / 2)

# Calculate the Butterworth filter coefficients
b, a = butter(order, normalized_cutoff, btype='low', analog=False)

# Print the coefficients
print("b coefficients:", b)
print("a coefficients:", a)

# Frequency response of the filter
w, h = freqz(b, a, worN=8000)
freq = w * fs / (2 * np.pi)

# Plot the frequency response
plt.figure(figsize=(8, 6))
plt.plot(freq,(abs(h)), 'b')# 20 * np.log10s
plt.ylabel('Amplitude Response (dB)')
plt.xlabel('Frequency (Hz)')
plt.title('Butterworth Filter Frequency Response')
plt.grid()

df = pd.read_csv("measurements/fft_output.txt")
fft = df['mag']

fft_out = filtfilt(b,a,fft)

filtered_fft = np.zeros_like(fft)
# Apply the Butterworth filter using a loop
for i in range(len(b),len(fft)):

    for j in range(1,len(a)):
        filtered_fft[i] += b[0] *fft[i]

        filtered_fft[i] -= a[j] * filtered_fft[i - j] 
        filtered_fft[i] += b[j] * fft[i - j] 

fft_out = filtered_fft
filtered_fft = np.zeros_like(fft_out)
# Apply the Butterworth filter using a loop
for i in range(len(fft)-3,0,-1):

    for j in range(1,len(a)):
        filtered_fft[i] += b[0] *fft_out[i]

        filtered_fft[i] -= a[j] * filtered_fft[i + j] 
        filtered_fft[i] += b[j] * fft_out[i + j] 


freq = np.linspace(0,200,len(fft))
plt.figure()
plt.plot(freq,fft)
plt.plot(freq,fft_out)
plt.plot(freq,filtered_fft)
plt.show()