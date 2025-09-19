import pandas as pd
import json
import os
from tqdm import tqdm

DATA_DIR = "./data/"

def load_all_jsonl_data(data_dir):
    all_data = []
    file_numbers = range(1, 6) # part1.jsonl to part5.jsonl

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
    return df

if __name__ == '__main__':
    # Adjust the DATA_DIR path correctly if running from a different location
    # For this task, it's relative to the current working directory, which is fine.
    df = load_all_jsonl_data(os.path.join(os.path.dirname(__file__), DATA_DIR))
    print(df.head())
    print(f"Loaded {len(df)} records.")
    
    # Optional: Sample 10% of the DataFrame for quicker validation, if needed
    # sampled_df = df.sample(frac=0.1, random_state=42)
    # print(f"Sampled down to {len(sampled_df)} records (10% of original) for quicker validation.")
    # print("Data loading and sampling complete.")
