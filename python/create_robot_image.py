import matplotlib.pyplot as plt
from utils import *
import pandas as pd
import numpy as np
import cv2


def extract_subframe(video_path, timestamp, output_path, x1, y1, x2, y2):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    # Convert timestamp (in seconds) to the corresponding frame number
    fps = video.get(cv2.CAP_PROP_FPS)  # Frames per second
    frame_number = int(fps * timestamp)
    
    # Set the video position to the frame
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    success, frame = video.read()
    if not success:
        print("Error: Unable to read the frame at the specified timestamp.")
        video.release()
        return
    
    # Crop the subframe (rectangle from x1, y1 to x2, y2)
    subframe = frame[y1:y2, x1:x2]
    
    # Save the subframe as a PNG image
    cv2.imwrite(output_path, subframe)
    print(f"Subframe extracted and saved as {output_path}")
    
    # Release the video
    video.release()

df = pd.read_csv('/home/thiemenrug/Documents/mrr/7_rovs/' + "Umin_11.csv")
video = '/home/thiemenrug/Documents/mrr/7_rovs/' + "7_rov_exp_11.mp4"

print(df)

# Example usage
video_file = video  # Path to the input video
timestamp_in_seconds = 5.0  # Time in seconds to extract the frame
output_image = "frame_at_5s.png"  # Path to save the extracted frame

extract_subframe(video_file, timestamp_in_seconds, output_image,490,80,1480,1070)
