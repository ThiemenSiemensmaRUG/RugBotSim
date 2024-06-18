import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("measurements/freq_mag_output.txt")

plt.figure()



plt.hist(df['freq'],weights=df['mag'],bins =100)
plt.show()