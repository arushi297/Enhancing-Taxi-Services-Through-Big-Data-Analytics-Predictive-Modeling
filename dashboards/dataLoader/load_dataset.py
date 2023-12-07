import pandas as pd
import sqlite3

# Load the taxi zone look up data into a pandas DataFrame
taxi_zone_lookup_filepath = '../data/dataFiles/taxi+_zone_lookup.csv'
taxi_zone_df = pd.read_csv(taxi_zone_lookup_filepath)

# Load the yellow trip data for sept 23 into a pandas DataFrame
yellow_tripdata_filepath =  '../data/dataFiles/yellow_tripdata_2023-09.parquet'
yellow_trip_df = pd.read_parquet(yellow_tripdata_filepath)

# Load the green trip data for sept 23 into a pandas DataFrame
green_tripdata_filepath =  '../data/dataFiles/green_tripdata_2023-09.parquet'
green_trip_df = pd.read_parquet(green_tripdata_filepath)

# Load the high vol fhv trip data for sept 23 into a pandas DataFrame
fhvhv_tripdata_filepath =  '../data/dataFiles/fhvhv_tripdata_2023-09.parquet'
fhvhv_trip_df = pd.read_parquet(fhvhv_tripdata_filepath)

# Connect to SQLite database (or create it if not exists)
db_path = 'nyc_taxi_database.db'
connection = sqlite3.connect(db_path)

# Create a taxi zone lookup table based on the DataFrame columns
table_name = 'taxi_zone_lookup'
taxi_zone_df.to_sql(table_name, connection, index=False, if_exists='replace')

# Create a yellow trip table based on the DataFrame columns
table_name = 'yellow_tripdata'
yellow_trip_df.to_sql(table_name, connection, index=False, if_exists='replace')

# Create a green trip table based on the DataFrame columns
table_name = 'green_tripdata'
green_trip_df.to_sql(table_name, connection, index=False, if_exists='replace')

# Commit the changes and close the connection
connection.commit()
connection.close()