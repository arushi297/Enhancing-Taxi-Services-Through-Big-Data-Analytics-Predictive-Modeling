import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import geopandas as gpd
import matplotlib.pyplot as plt


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

def connect_to_database():
    # Connect to SQLite database
    connection = sqlite3.connect('nyc_taxi_database.db')
    return connection
    

def ride_sharing_preference_map(connection):
    st.markdown("<h2 class='title'>Ride Sharing Preference based on Location</h2>", unsafe_allow_html=True)

    # Load the shapefile
    shapefile_path = "data/dataFiles/taxi_zones/taxi_zones.shp"
    gdf = gpd.read_file(shapefile_path)

    # Execute SQL query and fetch data
    query = """
    SELECT
        tz.LocationID,
        tz.Borough,
        tz.Zone,
        COALESCE(COUNT(CASE WHEN yt.Passenger_count = 1 THEN 1 END), 0) AS IndividualRides,
        COALESCE(COUNT(CASE WHEN yt.Passenger_count > 1 THEN 1 END), 0) AS SharedRides,
        COALESCE(MAX(yt.Passenger_count), 0) AS MaxPassengerCount,
        CASE
            WHEN COALESCE(SUM(CASE WHEN yt.Passenger_count > 1 THEN 1 ELSE 0 END), 0) = 0 THEN 0
            ELSE (COALESCE(SUM(CASE WHEN yt.Passenger_count > 1 THEN 1 ELSE 0 END), 0) * 100.0) / COALESCE(SUM(CASE WHEN yt.Passenger_count > 0 THEN 1 ELSE 0 END), 1)
        END AS SharedPercentage
    FROM
        taxi_zone_lookup tz
    LEFT JOIN
        yellow_tripdata yt ON yt.PULocationID = tz.LocationID
    GROUP BY
        tz.LocationID, tz.Borough, tz.Zone
    HAVING
        SharedPercentage > 0 AND SharedPercentage < 100;
    """

    # Fetch data from the database
    data = pd.read_sql_query(query, connection)

    # Merge the data with the GeoDataFrame
    merged_gdf = gdf.merge(data, how='left', left_on='LocationID', right_on='LocationID')

    # Highlight top 5 locations with the highest ride-sharing in one color
    top5_high = merged_gdf.nlargest(5, 'SharedPercentage')
    top5_high['highlight_color'] = 'green'

    # Highlight top 5 locations with the lowest ride-sharing in another color
    top5_low = merged_gdf.nsmallest(5, 'SharedPercentage')
    top5_low['highlight_color'] = 'red'

    # Combine the highlighted DataFrames
    highlighted_gdf = pd.concat([top5_high, top5_low])

    # Dynamic colormap selection
    colormap = st.selectbox("Select Colormap:", ["viridis", "plasma", "inferno", "magma", "cividis", "coolwarm"])

    # Plot the geolocation chart using matplotlib with dynamic colormap
    fig, ax = plt.subplots(figsize=(12, 8))
    merged_gdf.plot(ax=ax, column='SharedPercentage', cmap=colormap, legend=True, edgecolor='0.8')
    highlighted_gdf.plot(ax=ax, color=highlighted_gdf['highlight_color'], edgecolor='black', markersize=50, alpha=0.7)

    # Mark only the Location ID on the map with a light color
    for idx, row in highlighted_gdf.iterrows():
        # Use the centroid of the Polygon
        centroid = row['geometry'].centroid
        ax.text(centroid.x, centroid.y, f"{row['LocationID']}", ha='center', fontsize=8, color='lightgray')

    # Set plot title and labels
    plt.title('NYC Taxi Zones - Ride Sharing Percentage', fontsize=16)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Show the plot
    st.pyplot(fig)

    # Print the top 5 high and low locations with sharing percentages including Location ID
    st.subheader('Top 5 Locations with Highest Ride Sharing Percentage:')
    st.table(top5_high[['LocationID', 'Zone', 'Borough', 'SharedPercentage']].reset_index(drop=True))

    st.subheader("📍 Staten Island has the highest adoption of ride sharing.")

    st.subheader('Top 5 Locations with Lowest Ride Sharing Percentage:')
    st.table(top5_low[['LocationID', 'Zone', 'Borough', 'SharedPercentage']].reset_index(drop=True))

    st.subheader("📍 Bronx doesn't prefer ride sharing.")

    st.write("""
    **Insights:**
    1. **High Adoption in Staten Island:** The data reveals that Staten Island dominates the top locations with the highest ride-sharing percentages, indicating a 
    strong community preference for shared transportation.

    2. **Low Adoption in Bronx:** On the contrary, Bronx neighborhoods consistently appear among the lowest ride-sharing percentages, suggesting a lower adoption of 
    shared rides in these areas.

    3. **Guiding Interventions:** This information can guide targeted interventions and marketing efforts to promote ride-sharing in specific boroughs and 
    neighborhoods for improved efficiency and sustainability.
    """)


def payment_type_distribution(connection):
    st.markdown("<h2 class='title'>Customer Payment Type Preference Analysis</h2>", unsafe_allow_html=True)
    # Execute SQL query and load results into a DataFrame
    query = f"""
        SELECT 
            CASE 
                WHEN payment_type = 1 THEN 'Credit Card'
                WHEN payment_type = 2 THEN 'Cash'
                ELSE 'Others'
            END as PaymentCategory,
            COUNT(*) as Count
        FROM yellow_tripdata
        GROUP BY PaymentCategory
    """
    # Execute the query and fetch results
    result = pd.read_sql_query(query, connection)

    st.subheader("💳 Credit Card is the most preferred mode of payment among customers")

    # Plot using Plotly Express
    fig = px.pie(result, names='PaymentCategory', values='Count', title='Payment Type Distribution',
                labels={'PaymentCategory': 'Payment Type'}, hole=0.3)
    st.plotly_chart(fig)


def payment_type_by_location(connection):
    st.markdown("<h2 class='title'>Customer Payment Type Preference by Pickup Location</h2>", unsafe_allow_html=True)

    # Execute SQL query and load results into a DataFrame
    query = """
        SELECT 
            tzl.Borough,
            CASE 
                WHEN ytd.Payment_type = 1 THEN 'Credit Card'
                WHEN ytd.Payment_type = 2 THEN 'Cash'
                ELSE 'Others (No charge, Dispute, Unknown, Voided trip)'
            END as PaymentCategory,
            COUNT(*) as Count
        FROM yellow_tripdata ytd
        JOIN taxi_zone_lookup tzl ON ytd.PULocationID = tzl.LocationID
        GROUP BY tzl.Borough, PaymentCategory;
    """
    # Execute the query and fetch results
    result = pd.read_sql_query(query, connection)

    # Calculate percentage for each payment category within each pickup location
    result['Percentage'] = result.groupby('Borough')['Count'].transform(lambda x: x / x.sum() * 100)

    # Plot using Plotly Express with a bigger size and logarithmic y-axis scale
    fig = px.bar(result, x='Borough', y='Count', color='PaymentCategory', barmode='group',
                labels={'Borough': 'Pickup Location', 'Count': 'Count'},
                title='Payment Type Distribution by Pickup Location (Logarithmic Scale)')

    # Set the size of the chart
    fig.update_layout(
        barmode='group',
        xaxis_title='Pickup Location',
        yaxis_title='Count (Logarithmic Scale)',
        height=800,  # Set the height to a larger value
        width=1200,   # Set the width to a larger value
        yaxis_type="log"  # Set the y-axis to a logarithmic scale
    )

    st.plotly_chart(fig)

    st.write("""
    **Insights:**
    1. **Credit Card Dominance:** A majority of customers prefer payment via Credit Card, indicating a strong preference for electronic transactions.

    2. **Cash Transactions:** Following Credit Card payments, cash transactions are the second most popular, suggesting a significant portion of customers
     still prefer traditional payment methods.

    3. **Business Considerations:** Understanding these payment preferences can guide businesses in tailoring their payment options to meet customer demands,
     potentially enhancing customer satisfaction and streamlining transaction processes.
    """)


def spending_patterns_map(connection):
    st.markdown("<h2 class='title'>Customer Spending Patterns based on their Location</h2>", unsafe_allow_html=True)

    # Load the shapefile
    shapefile_path = "data/dataFiles/taxi_zones/taxi_zones.shp"
    gdf = gpd.read_file(shapefile_path)

    # Execute SQL query and fetch data
    query = """
    SELECT
        tz.LocationID,
        tz.Borough,
        tz.Zone,
        COALESCE(AVG(yt.total_amount), 0) AS AvgTotalSpendingAmount
    FROM
        taxi_zone_lookup tz
    LEFT JOIN
        yellow_tripdata yt ON yt.PULocationID = tz.LocationID
    GROUP BY
        tz.LocationID, tz.Borough, tz.Zone
    HAVING
        AvgTotalSpendingAmount > 0;  -- Exclude locations with AvgTotalSpendingAmount of 0
    """

    # Fetch data from the database
    data = pd.read_sql_query(query, connection)

    # Close SQLite connection
    connection.close()

    # Merge the data with the GeoDataFrame
    merged_gdf = gdf.merge(data, how='left', left_on='LocationID', right_on='LocationID')

    # Highlight top 5 locations with the highest average spending in one color
    top5_high = merged_gdf.nlargest(5, 'AvgTotalSpendingAmount')
    top5_high['highlight_color'] = 'green'

    # Highlight top 5 locations with the lowest average spending in another color
    top5_low = merged_gdf.nsmallest(5, 'AvgTotalSpendingAmount')
    top5_low['highlight_color'] = 'red'

    # Combine the highlighted DataFrames
    highlighted_gdf = pd.concat([top5_high, top5_low])

    # Dynamic colormap selection
    colormap_ = st.selectbox("Select Colormap:", ["inferno", "viridis", "plasma", "magma", "cividis", "coolwarm"])

    # Plot the geolocation chart using matplotlib with dynamic colormap
    fig, ax = plt.subplots(figsize=(12, 8))
    merged_gdf.plot(ax=ax, column='AvgTotalSpendingAmount', cmap=colormap_, legend=True, edgecolor='0.8')
    highlighted_gdf.plot(ax=ax, color=highlighted_gdf['highlight_color'], edgecolor='black', markersize=50, alpha=0.7)

    # Mark only the Location ID on the map with a light color
    for idx, row in highlighted_gdf.iterrows():
        # Use the centroid of the Polygon
        centroid = row['geometry'].centroid
        ax.text(centroid.x, centroid.y, f"{row['LocationID']}", ha='center', fontsize=8, color='lightgray')

    # Set plot title and labels
    plt.title('NYC Taxi Zones - Average Total Spending Amount', fontsize=16)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Show the plot
    st.pyplot(fig)

    # Print the top 5 high and low locations with average total amount including Location ID
    st.subheader('Top 5 Locations with Highest Average Total Spending:')
    st.table(top5_high[['LocationID', 'Zone', 'Borough', 'AvgTotalSpendingAmount']].reset_index(drop=True))

    st.subheader("📍 Staten Island and Newark are the locations with highest average spending")

    st.subheader('Top 5 Locations with Lowest Average Total Spending:')
    st.table(top5_low[['LocationID', 'Zone', 'Borough', 'AvgTotalSpendingAmount']].reset_index(drop=True))

    st.subheader("📍 Queens and Manhattan have the lowest average spending")

    st.write("""
    **Insights:**
    1. **High Spending Areas:** Westerleigh and Charleston/Tottenville in Staten Island lead in average total spending, suggesting thriving economic hubs. 
    This might indicate that people in these areas often travel to farther destinations or engage in higher-value transactions. Interestingly, some of these 
    locations also show a higher preference for ride-sharing, aligning with the notion of shared rides for longer or more expensive trips.

    2. **Low Spending Areas:** The locations with the lowest average total spending, spanning Staten Island, Queens, and Manhattan, showcase diverse economic 
    dynamics and consumer behaviors across boroughs. Lower spending in certain areas may suggest more frequent use for nearby trips.

    3. **Addressing Disparities:** The observed disparities underscore the need for strategic economic initiatives and business approaches tailored to the 
    specific needs and preferences of consumers in different locations. Understanding travel patterns can aid in optimizing services for both shorter and 
    longer-distance trips.
    """)


def main():
    connection = connect_to_database()

    st.markdown("<h1 class='title'>Customer Behavior Dashboard</h1>", unsafe_allow_html=True)

    # Plotting each chart from the main function
    ride_sharing_preference_map(connection)
    payment_type_distribution(connection)
    payment_type_by_location(connection)
    spending_patterns_map(connection)

    # Close SQLite connection
    connection.close()


if __name__ == "__main__":
    main()
