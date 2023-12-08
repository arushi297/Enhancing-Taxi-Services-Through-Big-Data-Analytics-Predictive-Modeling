import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import folium
import geopandas as gpd
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

def predict_taxi_demand(connection):
    # SQL query to filter data for day_of_the_month = 28.0
    query = '''
        SELECT
            hour_of_day,
            prediction
        FROM
            time_prediction
        WHERE
            day_of_the_month = 28.0;
    '''

    # Execute the query and load results into a DataFrame
    filtered_data = pd.read_sql_query(query, connection)

    # Streamlit app
    st.markdown("<h2 class='title'>Predicted Future Taxi Demand in Specific Areas and Times</h2>", unsafe_allow_html=True)

    
    
    custom_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#34495e', '#1abc9c', '#d35400']
    
    fig = px.bar(
        filtered_data,
        x='hour_of_day',
        y='prediction',
        labels={'prediction': 'Predicted Taxi Demand'},
        title='Predicted Taxi Demand for a specific day',
        color_discrete_sequence=custom_colors,
    )

    # Adjust layout for better appearance
    fig.update_layout(
        xaxis_title='Hour of Day',
        yaxis_title='Predicted Taxi Demand',
        showlegend=False,  # Hide legend if not needed
        plot_bgcolor='white',  # Set background color
    )

    # Update bar color and opacity
    fig.update_traces(marker_color='#3498db', opacity=0.8)

    # Show the plot
    st.plotly_chart(fig)

    
    ############# _PREDICTION_MAP_  ######################

    location_query = '''
        SELECT
            l.hour_of_day,
            l.day_of_the_month,
            l.fare_range,
            l.trip_distance_range,
            l.loction_trip_count,
            l.prediction,
            l.PULocationID,
            tz.Zone
           
        FROM
            location_prediction l
        JOIN
            taxi_zone_lookup tz
        ON
            l.PULocationID = tz.LocationID;
    '''

    # Execute the query and load results into a DataFrame
    joined_data = pd.read_sql_query(location_query, connection)

    # Load the GeoJSON data.
    geojson_data = gpd.read_file("/Users/chandanatj/streamlit-sales-dashboard/NYC Taxi Zones.geojson")

    # NYC GeoJSON
    nyc_geo = geojson_data


    # Display the Folium map using st.components.v1.html
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

    # Choropleth for Predicted Taxi Demand
    folium.Choropleth(
        geo_data=nyc_geo,
        name="choropleth",
        data=joined_data,
        columns=["Zone", "prediction"],
        key_on="feature.properties.zone",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Predicted Taxi Demand",
    ).add_to(m)

    # Layer Control
    folium.LayerControl().add_to(m)

    # Display the Folium map using st.components.v1.html
    # Check if the DataFrame is not None and not empty
    if joined_data is not None and not joined_data.empty:
        #st.write("Prediction of Taxi Demand in Specific Areas:")
        st.markdown("#### Predicted Taxi Demand by Area - Map")
        st.markdown("This map displays the predicted taxi demand in specific areas.")
        st.markdown("Zoom in and click on the map to explore predictions.")
        st.markdown("")
        folium_static(m, width=800, height=600)
    else:
        st.warning("No valid data available for the specified query.")


    ######################### PREDICTION_BAR_CHART ###############################
    borough_query = '''
        SELECT
            l.prediction,
            tz.Borough
        FROM
            location_prediction l
        JOIN
            taxi_zone_lookup tz
        ON
            l.PULocationID = tz.LocationID;
    '''

    # Execute the query and load results into a DataFrame
    borough_query_data = pd.read_sql_query(borough_query, connection)


    # Custom colors for the bar chart
    custom_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#34495e', '#1abc9c', '#d35400']

    # Plot bar chart
    fig = px.bar(
        borough_query_data,
        x='prediction',
        y='Borough',
        labels={'prediction': 'Predicted Taxi Demand'},
        title='Predicted Taxi Demand by Area',
        color_discrete_sequence=custom_colors,
    )

    # Adjust layout for better appearance
    fig.update_layout(
        xaxis_title='Predicted Taxi Demand',
        yaxis_title='Borough',
        showlegend=False,  # Hide legend if not needed
        plot_bgcolor='white',  # Set background color
    )

    # Update bar color and opacity
    fig.update_traces(marker_color='#3498db', opacity=0.8)

    # Show the plot
    st.plotly_chart(fig)


    



def main():

    st.markdown("<h1 class='title'>Predictive Models</h1>", unsafe_allow_html=True)

    # Connect to the database
    connection = sqlite3.connect('nyc_taxi_database.db')

    # Call the plot function with the database connection
    predict_taxi_demand(connection)


    # Close the database connection
    connection.close()


if __name__ == "__main__":
    main()


