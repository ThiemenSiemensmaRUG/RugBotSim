import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from webots_log_processor import WebotsProcessor







outputdir = "/home/thiemenrug/Desktop/parallel_1/"
instance=0
filename = f"Instance_{instance}/webots_log_{instance}.txt"
file = outputdir + filename
times = []
acc = []
for i in range(100):
    filename = f"Instance_{i}/webots_log_{i}.txt"
    file = outputdir + filename
    p = WebotsProcessor(file)

    t,a = p.get_dec_time_acc()
    acc.append(a)
    times.append(t)
print(np.array(acc).mean(),np.array(times).mean())