import pandas as pd
import json
import os
from tqdm import tqdm

DATA_DIR = "./data/"

def load_all_jsonl_data(data_dir):
    all_data = []
    file_numbers = range(1, 6) # part1.jsonl to part5.jsonl
    # file_numbers = range(1, 1) # part1.jsonl to part5.jsonl

    # Ensure the data directory exists, though files are already expected to be there
    if not os.path.isdir(data_dir):
        print(f"Error: Data directory '{data_dir}' not found.")
        return pd.DataFrame()

    for i in file_numbers:
        file_name = f"sewer-inspections-part{i}.jsonl"
        local_file_path = os.path.join(data_dir, file_name)
        
        if os.path.exists(local_file_path):
            print(f"Loading data from {local_file_path}...")
            # Using 'tqdm' for a progress bar, assuming files can be large
            with open(local_file_path, 'r') as f:
                for line in tqdm(f, desc=f"Loading {file_name}"):
                    all_data.append(json.loads(line))
        else:
            print(f"Skipping {file_name}: file not found at {local_file_path}.")

    df = pd.DataFrame(all_data)
    print(f"Finished loading a total of {len(df)} records from all files.")

    def flatten_dict_column(df_to_flatten, column_name):
        # Normalize the dictionary column. This expands it into a new DataFrame.
        # errors='ignore' ensures that non-dict values are kept as NaN.
        normalized_df = pd.json_normalize(df_to_flatten[column_name], errors='ignore')
        
        # Check if normalization actually produced new columns
        if not normalized_df.empty and len(normalized_df.columns) > 0:
            # Prefix new column names with the original column name
            normalized_df.columns = [
                f"{column_name}_{sub_col}" for sub_col in normalized_df.columns
            ]
            # Drop the original dictionary column
            df_to_flatten = df_to_flatten.drop(columns=[column_name])
            # Concatenate the new columns with the original DataFrame
            df_to_flatten = pd.concat([df_to_flatten, normalized_df], axis=1)
        return df_to_flatten

    # Identify and flatten columns that contain dictionaries
    for col in df.columns:
        # Check if the column contains dictionaries. Sample the first few non-nulls.
        # Use .apply(type) == dict to check for actual dict types efficiently.
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            print(f"Flattening column: {col}")
            df = flatten_dict_column(df, col)
            
    # Handle nested GPS dictionary if it exists after initial flattening
    if 'location_gps' in df.columns:
        print("Flattening nested 'location_gps' column...")
        df = flatten_dict_column(df, 'location_gps')

    return df

if __name__ == '__main__':
    # Adjust the DATA_DIR path correctly if running from a different location
    # For this task, it's relative to the current working directory, which is fine.
    df = load_all_jsonl_data(os.path.join(os.path.dirname(__file__), DATA_DIR))
    print(df.head())
    print(f"Loaded {len(df)} records.")
    # Optional: Save to CSV for quick inspection if needed
    # only save the first 100 rows to avoid large files
    df.head(100).to_csv("loaded_sewer_inspections.csv", index=False)
    print("Data loading and processing complete.")
    
    # Optional: Sample 10% of the DataFrame for quicker validation, if needed
    # (Note: Sampling after flattening is generally better for accurate representation
    # if the agent needs access to the full, flattened schema for testing.)
    # sampled_df = df.sample(frac=0.1, random_state=42)
    # print(f"Sampled down to {len(sampled_df)} records (10% of original) for quicker validation.")
    # print("Data loading and sampling complete.")
