import pandas as pd
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")

print("Script directory:", script_dir)
print("Data directory:", data_dir)
print("Files in data/:", os.listdir(data_dir) if os.path.exists(data_dir) else "data folder not found")

training_path = os.path.join(data_dir, "training_data.csv")
if os.path.exists(training_path):
    df = pd.read_csv(training_path)
    print(f"\nDataset shape: {df.shape}")
    print(f"Column count: {len(df.columns)}")
    print(f"\nLast column (target): {df.columns[-1]}")
    
    conditions = sorted(df.iloc[:, -1].unique().tolist())
    print(f"\nTotal unique conditions: {len(conditions)}")
    print("\nConditions list:")
    for i, c in enumerate(conditions, 1):
        print(f"{i}. {c}")
else:
    print("training_data.csv not found!")
