import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter,filtfilt

def butter_lowpass_filter(data, cutoff_freq, fs, order):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


df_1 = pd.read_csv("measurements/fft_output.txt")
freqs = np.linspace(0,100,len(df_1))
df_2 = pd.read_csv("measurements/fft_filtered.txt")

plt.figure()
plt.plot(freqs,df_1['mag'])
plt.plot(freqs,df_2['mag'])
plt.show()

df = pd.read_csv("measurements/fft_output.txt")

df_in = pd.read_csv("measurements/acc_x50_y50 copy.txt",header=0)
data= np.array(df_in['acc'])[100:]
window = np.hanning(len(data))

fft_result = np.fft.fft(data)
n = len(fft_result)
fft_acc_z = np.abs(np.fft.fft(data)[1:n//2])
freq = (np.fft.fftfreq(n, d=1/200)[1:n//2])
complex_numbers = np.abs([complex(r, i) for r, i in zip(df['Real'], df['Imaginary'])])[1:n//2]


inputs =  np.abs([complex(r, i) for r, i in zip(df['Real'], df['Imaginary'])])[1:n//2]
filtered_data = butter_lowpass_filter(complex_numbers, 15, 200, 1)
index = []
i=0
#pick peaks in filtered fft
for i in range(1,len(filtered_data)-5):
    if (filtered_data[i-1] < filtered_data[i]) and (filtered_data[i+1] < filtered_data[i]):
        index.append(i)

N_peaks = 5
top_indices = sorted(index, key=lambda i: abs(complex_numbers[i]), reverse=True)[:N_peaks]
top_peaks = [complex_numbers[i] for i in top_indices]




# Plot FFT result
plt.figure(figsize=(8, 6))
plt.plot(freq,complex_numbers)
plt.plot(freq, filtered_data)

plt.scatter(freq[top_indices],top_peaks,c ='r')
plt.title('FFT Result')
plt.xlabel('Frequency')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()