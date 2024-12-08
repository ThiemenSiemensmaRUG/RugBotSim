import os
import random
import math
from matplotlib import pyplot as plt

# Constants
SAMPLE_FREQ = 200.0  # Sample rate in Hz
SAMPLE_LENGTH = 4.5  # Sample length in seconds
N_SAMPLES = int(SAMPLE_FREQ * SAMPLE_LENGTH)


def generate_file(filepath, n_samples, pos_x, pos_y):
    with open(filepath, 'w') as file:
        for i in range(n_samples):
            t = i / SAMPLE_FREQ
            data_point = (math.sin(SAMPLE_FREQ * t) * 0.5 * (-math.cos((math.pi * pos_y) / 50) + 1)) # Function
            data_point += random.gauss(0, 0.01) # Noise
            file.write(f"{data_point}\n")


def main():
    base_dir = "measurements"

    # Ensure the base directory exists
    os.makedirs(base_dir, exist_ok=True)

    positions = [(x, y) for x in range(0, 110, 10) for y in range(0, 110, 10)]

    for pos_x, pos_y in positions:
        filename = f"acc_x{pos_x}_y{pos_y}.txt"
        filepath = os.path.join(base_dir, filename)
        generate_file(filepath, N_SAMPLES, pos_x, pos_y)

    print(f"Dummy data files generated in directory: {base_dir}")

if __name__ == "__main__":
    main()