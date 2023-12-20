# Enhancing Taxi Services Through Big Data Analytics and Predictive Modeling

## Introduction
This project aims to enhance taxi services through big data analytics and predictive modeling. It includes dashboards for customer behavior, fare price prediction, geospatial demand and supply, prediction models, revenue analysis, trip duration prediction, and vendor comparison.

## How to Run

To run the project, make sure you have Streamlit installed. You can install it using:

```bash
pip install streamlit
```
Once installed, you can run the application using the following command:
```
streamlit run path/to/Home.py
```

## Repository Structure

- `dashboards/`
  - `data/`
    - `datafiles/`
      - `NYC Taxi Zones.geojson` - GeoJSON file for NYC taxi zones.
      - `green_tripdata_2023-09.parquet` - Parquet file for green taxi trip data in September 2023.
      - `taxi+_zone_lookup.csv` - CSV file for taxi zone lookup.
      - `taxi_pref.csv` - CSV file for taxi preferences.
      - `taxi_stats.csv` - CSV file for taxi statistics.
      - `yellow_tripdata_2023-09.parquet` - Parquet file for yellow taxi trip data in September 2023.
      - `taxi_zones/`
        - `taxi_zones.dbf` - Database file for taxi zones.
        - `taxi_zones.prj` - Projection file for taxi zones.
        - `taxi_zones.sbntaxi_zones.sbx` - Index file for taxi zones.
        - `taxi_zones.shp` - Shapefile for taxi zones.
        - `taxi_zones.shp.xml` - XML file for taxi zones.
        - `taxi_zones.shx` - Index file for taxi zones.
  - `dataLoader/`
    - `create_taxi_stats_table.py` - Python script to create taxi statistics table.
    - `load_dataset.py` - Python script to load the dataset.
    - `load_dataset_fhv.py` - Python script to load FHV dataset.
    - `queries/`
      - `taxi_perf_stats_query.txt` - Query file for taxi performance statistics.
      - `taxi_preference_query.txt` - Query file for taxi preferences.
  - `images/`
    - `taxi_image.jpg` - Image file for a taxi.
  - `pages/`
    - `Customer_Behavior_Dashboard.py` - Python script for the Customer Behavior Dashboard.
    - `Fare_Price_Prediction_Dashboard.py` - Python script for the Fare Price Prediction Dashboard.
    - `Geospatial_Demand_and_Supply_Dashboard.py` - Python script for the Geospatial Demand and Supply Dashboard.
    - `Prediction_Models.py` - Python script for prediction models.
    - `Revenue_Analysis_Dashboard.py` - Python script for the Revenue Analysis Dashboard.
    - `Trip_Duration_Prediction_Dashboard.py` - Python script for the Trip Duration Prediction Dashboard.
    - `Vendor_Comparison_Dashboard.py` - Python script for the Vendor Comparison Dashboard.
  - `Home.py` - Python script for the main dashboard.
- `predictions/`
  - `hourly_trip_predictor.ipynb` - Jupyter notebook for predicting hourly trips.
  - `location_wise_trip_predictor.ipynb` - Jupyter notebook for predicting location-wise trips.
  - `merge_csv.py` - Python script to merge CSV files.
  - `trip_duration_predictor.ipynb` - Jupyter notebook for predicting trip duration.
  - `trip_fare_predictor.ipynb` - Jupyter notebook for predicting trip fare.
- `README.md` - Markdown file providing information about the project.

## Demo Video

The project demo can be found [here](https://drive.google.com/file/d/1RgqfifhoaMTZegTxa05FoXP6XksU_5KI/view?usp=sharing).

## Authors

- **Arushi Arora**
  - Email: [aa10350@nyu.edu](mailto:aa10350@nyu.edu)

- **Saaketh Koundinya**
  - Email: [sg7729@nyu.edu](mailto:sg7729@nyu.edu)

- **Chandana**
  - Email: [ct3002@nyu.edu](mailto:ct3002@nyu.edu)
