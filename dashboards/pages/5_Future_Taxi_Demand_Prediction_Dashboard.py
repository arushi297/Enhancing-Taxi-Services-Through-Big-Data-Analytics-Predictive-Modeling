import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import geopandas as gpd
from streamlit_folium import folium_static
import sqlite3

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

def predict_taxi_demand():
    # Load data from CSV
    df_time_prediction = pd.read_csv('data/predictedData/hourly_pred.csv')
    df_location_prediction = pd.read_csv('data/predictedData/location_pred.csv')
    df_taxi_zone_lookup = pd.read_csv('data/dataFiles/taxi+_zone_lookup.csv')

    # Filter data for day_of_the_month = 28.0
    filtered_data = df_time_prediction[df_time_prediction['day_of_the_month'] == 28.0]

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
        showlegend=False,
        plot_bgcolor='white',
    )

    # Update bar color and opacity
    fig.update_traces(marker_color='#3498db', opacity=0.8)

    # Show the plot
    st.plotly_chart(fig)

    # Filtered data for location prediction
    joined_data = pd.merge(df_location_prediction, df_taxi_zone_lookup, how='inner', left_on='PULocationID', right_on='LocationID')

    # Load the GeoJSON data.
    geojson_data = gpd.read_file("data/dataFiles/NYC_Taxi_Zones.geojson")

    # NYC GeoJSON
    nyc_geo = geojson_data

    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

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

    folium.LayerControl().add_to(m)

    if not joined_data.empty:
        st.markdown("#### Predicted Taxi Demand by Area - Map")
        st.markdown("This map displays the predicted taxi demand in specific areas.")
        st.markdown("Zoom in and click on the map to explore predictions.")
        st.markdown("")
        folium_static(m, width=800, height=600)
    else:
        st.warning("No valid data available for the specified query.")
    
def plot_predicted_demand_by_borough(connection):
    try:
        # SQL query to join tables and filter data
        borough_query = '''
            SELECT
                tz.Borough,
                SUM(l.prediction) AS TotalPrediction
            FROM
                location_prediction l
            JOIN
                taxi_zone_lookup tz
            ON
                l.PULocationID = tz.LocationID
            GROUP BY
                tz.Borough;
        '''

        # Execute the query and load results into a DataFrame
        borough_query_data = pd.read_sql_query(borough_query, connection)

        # Custom colors for the bar chart
        custom_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#34495e', '#1abc9c', '#d35400']

        # Plot bar chart
        fig = px.bar(
            borough_query_data,
            x='TotalPrediction',  # Use the correct column name
            y='Borough',
            labels={'TotalPrediction': 'Predicted Taxi Demand'},
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

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def main():
    st.markdown("<h1 class='title'>Future Taxi Demand Prediction Dashboard</h1>", unsafe_allow_html=True)

    # Call the plot function with the CSV path
    predict_taxi_demand()

    # Connect to the database
    connection = sqlite3.connect('nyc_taxi_database.db')
    
    plot_predicted_demand_by_borough(connection)

    # Close the database connection
    connection.close()


if __name__ == "__main__":
    main()
