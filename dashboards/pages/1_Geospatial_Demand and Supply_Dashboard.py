import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
import numpy as np
from streamlit_folium import folium_static

# Apply custom CSS style for center-aligned titles
st.markdown(
    """
    <style>
        .title {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)


def plot_taxi_demand(connection):
    st.markdown("<h2 class='title'>Peak and Off-Peak Hours Taxi Demand Analysis</h2>", unsafe_allow_html=True)

    # Checkbox for taxi type selection
    selected_yellow = st.checkbox("Yellow Taxi", True, key="yellow_checkbox")
    selected_green = st.checkbox("Green Taxi", False, key="green_checkbox")

    # Radio buttons for date selection
    date_selection = st.radio("Select Date Range", ["Day", "Week", "Month"])

    # Execute SQL query and load results into a DataFrame
    query = '''
        SELECT
            tpep_pickup_datetime as pickup_datetime,
            'yellow' as taxi_type
        FROM
            yellow_tripdata
        UNION ALL
        SELECT
            lpep_pickup_datetime as pickup_datetime,
            'green' as taxi_type
        FROM
            green_tripdata;
    '''
    df = pd.read_sql_query(query, connection)

    # Ensure 'pickup_datetime' is in datetime format
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])

    # Apply taxi type filter after running the query
    selected_taxi_types = []
    if selected_yellow:
        selected_taxi_types.append('yellow')
    if selected_green:
        selected_taxi_types.append('green')

    df_filtered = df[df['taxi_type'].isin(selected_taxi_types)]

    if date_selection == "Day":
        selected_date = st.date_input("Select a Date", pd.Timestamp("2023-09-30"))
        df_filtered = df_filtered[df_filtered['pickup_datetime'].dt.date == selected_date]

    elif date_selection == "Week":
        # Set the default date range to the first week of September 2023
        start_date = st.date_input("Select Start Date", pd.Timestamp("2023-09-01"))
        end_date = st.date_input("Select End Date", pd.Timestamp("2023-09-07"))  # Assuming a week duration

        # Convert date range to datetime64[ns]
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter the DataFrame based on the selected date range
        df_filtered = df_filtered[(df_filtered['pickup_datetime'] >= start_date) & (df_filtered['pickup_datetime'] <= end_date)]

    elif date_selection == "Month":
        # Create a dropdown (selectbox) for the user to choose a month
        selected_month = st.selectbox("Select a Month", range(1, 13), format_func=lambda x: pd.to_datetime(str(x), format='%m').strftime('%B'), index=8)

        # Filter the DataFrame based on the selected month and year (assumed to be 2023)
        df_filtered = df_filtered[(df_filtered['pickup_datetime'].dt.month == selected_month) & (df_filtered['pickup_datetime'].dt.year == 2023)]

    # Create a column for the hour of the day
    df_filtered['pickup_hour'] = df_filtered['pickup_datetime'].dt.hour

    # Group by hour and calculate the number of trips
    hourly_demand = df_filtered.groupby(['pickup_hour', 'taxi_type']).size().reset_index(name='Number of Trips')

    # Plotting peak and off-peak hours
    fig = px.bar(hourly_demand, x='pickup_hour', y='Number of Trips', color='taxi_type',
                 labels={'pickup_hour': 'Hour of Day', 'Number of Trips': 'Number of Trips'},
                 title=f"Taxi Demand Analysis - {date_selection} ({', '.join(selected_taxi_types)})",
                 color_discrete_map={'yellow': 'yellow', 'green': 'green'})

    # Display the radio buttons, checkbox, and the plot
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⏰ 4-7 pm in the evening are the peak demand hours for the taxis")

    st.write("""
    **Insights:**

    **1. Peak Demand Hours (4-7 pm in the evening):** The 4-7 pm evening peak in taxi demand is primarily driven by the conclusion of the workday and rush hour commute.
     As people leave workplaces and engage in social or recreational activities, the need for efficient transportation surges. Taxis offer a convenient solution, 
     especially in inclement weather, contributing to the heightened demand during these hours.

    **2. Non-Peak Hours (2-5 am in the morning):** From 2-5 am, taxi demand hits its lowest point due to the closure of businesses and limited social activities. 
    Public transportation availability during these hours and safety concerns may divert individuals away from taxis. With fewer people commuting and engaging in 
    late-night activities, the overall demand diminishes during these non-peak hours.""")


def get_top_taxi_locations(connection):
    # Execute SQL query and load results into a DataFrame
    query = '''
        SELECT
            tz.LocationID,
            tz.Borough,
            tz.Zone,
            COUNT(*) AS TripCount
        FROM
            taxi_zone_lookup tz
        JOIN
            (
                SELECT PULocationID
                FROM yellow_tripdata
                UNION ALL
                SELECT PULocationID
                FROM green_tripdata
            ) AS combined_taxi
        ON
            tz.LocationID = combined_taxi.PULocationID
        GROUP BY
            tz.LocationID, tz.Borough, tz.Zone
        ORDER BY
            TripCount DESC;
    '''
    df = pd.read_sql_query(query, connection)

    # Load the GeoJSON data.
    geojson_data = gpd.read_file("../data/dataFiles/NYC Taxi Zones.geojson")
    #geojson_data = gpd.read_file("/Users/chandanatj/streamlit-sales-dashboard/NYC Taxi Zones.geojson")


    # NYC GeoJSON
    nyc_geo = geojson_data

    # Map
    # Your Folium map creation code here
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

    # Choropleth for Taxi Demand
    folium.Choropleth(
        geo_data=nyc_geo,
        name="choropleth",
        data=df,  # Assuming df has 'Zone' and 'TripCount' columns
        columns=["Zone", "TripCount"],
        key_on="feature.properties.zone",  # Adjust this based on your GeoJSON structure
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Taxi Demand",
    ).add_to(m)

    # Layer Control
    folium.LayerControl().add_to(m)

    # Display the map
    st.title(":car: Top Taxi Locations Dashboard")
    st.markdown("## Taxi Demand Map")

    # Check if the DataFrame is not None and not empty
    if df is not None and not df.empty:
        st.write("Areas with the highest demand for taxi services:")
        st.markdown("### Taxi Demand Map")
        st.markdown("This map displays the areas with the highest demand for taxi services.")
        st.markdown("Zoom in and click on the map to explore specific zones.")
        st.markdown("")

        # Display the Folium map using st.write
        folium_static(m, width=800, height=600)

    else:
        st.warning("No valid data available for the specified query.")

    # Display DataFrames
    st.subheader("Insights from Top Taxi Locations:")
    st.dataframe(df)

    # Display Key Insights
    st.subheader("Key Insights:")
    st.write(
        """
        1. **JFK Airport Dominates:** The location in Queens, specifically JFK Airport, 
        stands out as the busiest taxi location with a significantly high number of trips (159,376).
        
        2. **Manhattan Hotspots:** Several locations in Manhattan, such as Upper East Side South, 
        Midtown Center, and Upper East Side North , also show high trip counts.
        
        3. **LaGuardia Airport Presence:** LaGuardia Airport in Queens is another busy airport location, 
        though not as busy as JFK. It still manages to secure a significant number of taxi trips (100,988).
        
        4. **Diverse Locations:** The map reveals less frequented locations, including those in Staten Island and some locations, 
        such as Charleston/Tottenville in Staten Island, have very low trip counts (1).
          """
    )



def main():

    st.markdown("<h1 class='title'>Geospatial Demand and Supply Dashboard</h1>", unsafe_allow_html=True)

    # Connect to the database
    connection = sqlite3.connect('nyc_taxi_database.db')

    # Call the plot function with the database connection
    plot_taxi_demand(connection)

    get_top_taxi_locations(connection)

    # Close the database connection
    connection.close()


if __name__ == "__main__":
    main()
