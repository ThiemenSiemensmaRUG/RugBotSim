import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from _post_processing_utils import *




   

# Example usage
run = 1
instance = 1
processor = WebotsLogProcessor(run, instance)
processor.read_and_process_data()  # Process the data

mode1, curv1 = processor.compute_mode_shape(100)
processor.plot_density()
run = 1
# instance = 2
# processor = WebotsLogProcessor(run, instance)
# processor.read_and_process_data()  # Process the data
# mode2, curv2 = processor.compute_mode_shape(100)

# # plot_surface(processor.X, processor.Y, curv1 - curv2)



# Display the plot
plt.show()