import pandas as pd
import sqlite3

# Load the high vol fhv trip data for sept 23 into a pandas DataFrame
fhvhv_tripdata_filepath =  '../data/dataFiles/fhvhv_tripdata_2023-09.parquet'
fhvhv_trip_df = pd.read_parquet(fhvhv_tripdata_filepath)

# Connect to SQLite database (or create it if not exists)
db_path = 'nyc_taxi_database.db'
connection = sqlite3.connect(db_path)

# Create a high vol fhv trip table based on the DataFrame columns
table_name = 'fhvhv_tripdata'
fhvhv_trip_df.to_sql(table_name, connection, index=False, if_exists='replace')

# Commit the changes and close the connection
connection.commit()
connection.close()