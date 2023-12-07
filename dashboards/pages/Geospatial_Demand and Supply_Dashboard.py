import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

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


def main():

    st.markdown("<h1 class='title'>Geospatial Demand and Supply Dashboard</h1>", unsafe_allow_html=True)

    # Connect to the database
    connection = sqlite3.connect('nyc_taxi_database.db')

    # Call the plot function with the database connection
    plot_taxi_demand(connection)

    # Close the database connection
    connection.close()


if __name__ == "__main__":
    main()
