import numpy as np
from scipy.linalg import eig
from scipy.signal import welch
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('python/output_two_side_undamaged_5s.txt')
print(data['posz'].unique())
data = data.round({'time': 10, 'posx':3,'posy':3,'posz':3,'labels':0,'valuex':6,
                   'valuey':6,'valuez':6})

xgrid = np.linspace(-.4,.4,9)
ygrid = np.linspace(-.4,.4,9)


for x in xgrid:
    for y in ygrid:
        x = round(x,2)
        y = round(y,2)
        df = data[(data['posx'] == x) & (data['posy'] == y)]


        df = df[df['labels'] == df.iloc[0]['labels']]
        df = df.sort_values(['time'])
        print(x+0.5,y+0.5)
        print(round((x+0.5) * 100),round((y+0.5) * 100))
        
        acc = np.array(df.iloc[int(len(df)/10):]['valuez'])
        with open(f"measurements//acc_x{round((x+0.5)*100)}_y{round((y+0.5)*100)}.txt", 'w') as file:
            # Iterate through the array and write each number formatted as a decimal
            for number in acc:
                file.write(f"{number:.18f}\n")


