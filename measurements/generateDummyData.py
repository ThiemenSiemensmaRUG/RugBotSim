import os
import random

# Constants
SAMPLE_FREQ = 200.0  # Sample rate in Hz
SAMPLE_LENGTH = 4.5  # Sample length in seconds
N_SAMPLES = int(SAMPLE_FREQ * SAMPLE_LENGTH)


def generate_file(filepath, n_samples):
    with open(filepath, 'w') as file:
        for _ in range(n_samples):
            data_point = random.uniform(-1.0, 1.0)
            file.write(f"{data_point}\n")


def main():
    base_dir = "measurements"

    # Ensure the base directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Generate dummy data for a 1x1 m grid divided into 10x10 cm squares
    positions = [(x, y) for x in range(0, 110, 10) for y in range(0, 110, 10)]

    for pos_x, pos_y in positions:
        filename = f"acc_x{pos_x}_y{pos_y}.txt"
        filepath = os.path.join(base_dir, filename)
        generate_file(filepath, N_SAMPLES)

    print(f"Dummy data files generated in directory: {base_dir}")


if __name__ == "__main__":
    main()