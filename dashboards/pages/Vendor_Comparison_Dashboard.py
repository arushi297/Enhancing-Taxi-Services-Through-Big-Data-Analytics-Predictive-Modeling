import streamlit as st
import pandas as pd
import plotly.express as px
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

def load_taxi_data(filepath):
    return pd.read_csv(filepath)


def load_shapefile(filepath):
    return gpd.read_file(filepath)


def plot_avg_fare_per_distance(df_combined):
    st.markdown("<h2 class='title'>Comparing Taxi Services based on Average Fare Per Unit Distance</h2>", unsafe_allow_html=True)
    fig = px.bar(df_combined, x='Borough', y='AvgFarePerUnitDistance', color='Service', barmode='group')
    st.plotly_chart(fig)


def plot_avg_trip_time_per_distance(df_combined):
    st.markdown("<h2 class='title'>Comparing Taxi Services based on Average Trip Time Per Unit Distance</h2>", unsafe_allow_html=True)
    fig = px.bar(df_combined, x='Borough', y='AvgTripTimePerUnitDistance', color='Service', barmode='group')
    st.plotly_chart(fig)

    st.write("""
    **Insights:**

    **1. Average Fare Per Unit Distance:**
    - Green taxi has the lowest fare per unit distance in most boroughs.
    - Uber and Lyft have a comparative fare per unit distance, being the second lowest overall, except in Bronx and Brooklyn where Yellow taxi has the second 
    lowest fare.

    **2. Average Trip Time Per Unit Distance:**
    - Yellow and Green taxis have considerably higher trip time per unit distance.
    - Uber and Lyft have comparable trip times, which are presumably lower than those of Yellow and Green taxis.""")
    
    st.subheader("🚕 Uber and Lyft are considered to provide better services overall, as they offer a combination of comparable fares and lower trip times.")


def plot_geolocation_chart(gdf, result_df_max):
    st.markdown("<h2 class='title'>Taxi Service Dominance based on the Location</h2>", unsafe_allow_html=True)
    gdf = gdf.merge(result_df_max[['LocationID', 'Service']], on='LocationID', how='left')
    gdf['Service'] = gdf['Service'].fillna('NoService')

    colormap = st.selectbox("Select Colormap:", ["viridis", "plasma", "inferno", "magma", "cividis", "coolwarm"])

    fig, ax = plt.subplots()
    gdf.plot(ax=ax, cmap=colormap, legend=True, column='Service', categorical=True)
    st.pyplot(fig)

    st.subheader("🚕 Uber is the most preferred taxi service provider in most of the locations")

    selected_columns = ['LocationID', 'zone', 'borough', 'Service']
    selected_data = gdf[selected_columns]
    
    # Filter locations where Lyft is dominant
    lyft_locations = selected_data[selected_data['Service'] == 'Lyft']

    # Filter locations where service Yellow taxi is dominant
    yellow_taxi_locations = selected_data[selected_data['Service'] == 'Yellow taxi']

    # Display Lyft locations in a table
    st.write("Lyft Dominant Locations:")
    st.table(lyft_locations) 

    # Display Yellow taxi locations in a table
    st.write("Yellow Taxi Dominant Locations:")
    st.table(yellow_taxi_locations)  


def plot_rides_by_service_and_borough(result_df):
    st.markdown("<h2 class='title'>Number of Rides by Taxi Service and Borough</h2>", unsafe_allow_html=True)
    grouped_df = result_df.groupby(['Borough', 'Service']).sum().reset_index()
    fig = px.bar(grouped_df, x='Borough', y='NumberOfRides', color='Service', title='Number of Rides by Service and Borough')
    st.plotly_chart(fig)

    st.write("""
    **Insights:**

    1. **Uber Dominance and Regional Variations:** Uber's dominance suggests that it has successfully captured a significant market share in many locations. 
    This could be attributed to factors such as widespread availability, user-friendly app features, and competitive pricing. The presence of yellow taxis in 
    certain zones of Manhattan and Lyft in specific areas of Bronx/Brooklyn indicates that regional preferences and market segmentation exist. Different providers
    may appeal to various demographics or offer specialized services in these specific zones.

    2. **Lyft as the Second Preferred Option:** The fact that Lyft is the second preferred taxi service after Uber highlights its competitiveness in the market. 
    Customers may choose Lyft for reasons such as competitive pricing, perceived service quality, or unique features offered by Lyft that distinguish it from other 
    providers.

    3. **Green Taxi as the Least Preferred:** TThe information about green taxis being the least preferred suggests that customers may have reservations or concerns
    related to this particular service. Possible reasons could include a smaller fleet, limited coverage, or availability compared to Uber and Lyft.
    """)


def main():
    st.markdown("<h1 class='title'>Vendor Comparison Dashboard</h1>", unsafe_allow_html=True)

    # Load data
    taxi_stats_filepath = 'data/dataFiles/taxi_stats.csv'
    df_combined = load_taxi_data(taxi_stats_filepath)

    # Load shapefile
    shapefile_path = "data/dataFiles/taxi_zones/taxi_zones.shp"
    gdf = load_shapefile(shapefile_path)

    # Chart 1
    plot_avg_fare_per_distance(df_combined)

    # Chart 2
    plot_avg_trip_time_per_distance(df_combined)

    # Load data for geolocation chart
    taxi_pref_filepath = 'data/dataFiles/taxi_pref.csv'
    result_df = pd.read_csv(taxi_pref_filepath)

    # Find the service with the highest ride count for each location
    result_df_max = result_df.loc[result_df.groupby('LocationID')['NumberOfRides'].idxmax()]

    # Geolocation chart
    plot_geolocation_chart(gdf, result_df_max)

    # Rides by service and borough chart
    plot_rides_by_service_and_borough(result_df)


if __name__ == "__main__":
    main()