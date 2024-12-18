import numpy as np
import pandas as pd


def create_grid(df, tolerance):
    xunique = df['x'].unique()
    yunique = df['y'].unique()
    x_min, x_max = df['x'].min(), df['x'].max()
    y_min, y_max = df['y'].min(), df['y'].max()

    step_x = int((x_max - x_min) / tolerance)
    step_y = int((y_max - y_min) / tolerance)
    x_grid = np.linspace(x_min, x_max,step_x+1)
    y_grid = np.linspace(y_min, y_max, step_y+1)
    gridX, gridY = np.meshgrid(x_grid, y_grid)
    return gridX, gridY