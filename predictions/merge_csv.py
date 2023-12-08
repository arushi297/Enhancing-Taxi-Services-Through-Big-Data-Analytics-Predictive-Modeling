import os
import pandas as pd

# Set the path to the folder containing CSV files
folder_path = '/scratch/sg7729/Big data Project/hourly_predictions_sept.csv'

# Get a list of all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize an empty DataFrame to store the combined data
combined_data = pd.DataFrame()

# Loop through each CSV file and append its data to the combined_data DataFrame
for csv_file in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    df = pd.read_csv(file_path)
    combined_data = combined_data.append(df, ignore_index=True)

# Write the combined data to a new CSV file
combined_data.to_csv('/scratch/sg7729/Big data Project/hourly_pred.csv', index=False)

print("Combination completed.")
