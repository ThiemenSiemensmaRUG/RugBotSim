import numpy as np
import pandas as pd

import pandas as pd

def return_unique_node_positions_and_labels(df):
    print(df.columns)

    # Filter the DataFrame to only include unique label_num
    df_unique = df.drop_duplicates(subset=['# label_num'])

    # Select only the 'x', 'y', and 'label_num' columns
    df_unique = df_unique[['x', 'y', '# label_num']]
    df_unique['x'] = df_unique['x'] + 500
    df_unique['y'] = df_unique['y'] + 500
        # Convert all columns to integers, ensuring they are numeric first
    df_unique = df_unique.apply(pd.to_numeric, errors='coerce')  # Convert all columns to numeric, invalid parsing will be set as NaN
    df_unique = df_unique.fillna(0).astype(int)  # Replace NaNs with 0 and convert all to integers
    
    # Reset the index and drop the old index column
    df_unique = df_unique.reset_index(drop=True)
    return df_unique.copy()

def main():
    df_damaged = pd.read_csv("measurements/damaged/modal_shape.csv")
    df_undamaged = pd.read_csv("measurements/undamaged/modal_shape.csv")

    df_damaged = return_unique_node_positions_and_labels(df_damaged)
    df_undamaged = return_unique_node_positions_and_labels(df_undamaged)

    df_damaged.to_csv("measurements/damaged/_label_mapping.csv",index=False)
    df_undamaged.to_csv("measurements/undamaged/_label_mapping.csv",index=False)



if __name__ == "__main__":
    main()