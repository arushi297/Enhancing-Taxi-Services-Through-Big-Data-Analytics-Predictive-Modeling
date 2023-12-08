import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

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

# Define the trip duration threshold
trip_duration_threshold = 5

# Function to plot interactive heatmap for trip duration
def plot_heatmap_duration(df, lookup_df):
    st.markdown("<h2 class='title'>Predicted Trip Duration for Pickup and Dropoff Borough Location</h2>", unsafe_allow_html=True)
    # Merge with lookup table to get Borough for PU and DO LocationID
    df_merged = pd.merge(df, lookup_df[['LocationID', 'Borough']], left_on='PULocationID', right_on='LocationID', how='left')
    df_merged.rename(columns={'Borough': 'PUBorough'}, inplace=True)
    df_merged = pd.merge(df_merged, lookup_df[['LocationID', 'Borough']], left_on='DOLocationID', right_on='LocationID', how='left')
    df_merged.rename(columns={'Borough': 'DOBorough'}, inplace=True)

    # Filter out rows with small trip durations and specific days
    df_filtered = df_merged[
        (df_merged['prediction'] > trip_duration_threshold)
    ]

    # Group by PU and DO Borough and calculate mean of duration prediction
    grouped_df = df_filtered.groupby(['PUBorough', 'DOBorough']).mean().reset_index()

    # Create a heatmap using Plotly
    fig = go.Figure(go.Heatmap(
        z=grouped_df['prediction'],
        x=grouped_df['DOBorough'],
        y=grouped_df['PUBorough'],
        colorscale='YlGnBu',
        colorbar=dict(title='Mean Prediction of Trip Duration')
    ))

    # Customize layout
    fig.update_layout(
        title='Interactive Heatmap of Mean Trip Duration Predictions in minutes',
        xaxis=dict(title='Drop-off Borough'),
        yaxis=dict(title='Pick-up Borough')
    )

    # Show the interactive heatmap
    st.plotly_chart(fig)
    st.write("Darker heatmap color represents a longer trip duration")

# Function to plot scatter plot for trip duration
def plot_scatter_duration(df):
    filtered_df = df[(df['prediction'] > trip_duration_threshold)  & (df['trip_distance'] <= 40)]

    st.markdown("<h2 class='title'>Taxi Predicted Trip Duration vs Trip Distance</h2>", unsafe_allow_html=True)

    # Scatter plot
    st.write("**Trip Duration vs Predicted Trip Duration**")
    fig, ax = plt.subplots()
    ax.scatter(filtered_df['trip_distance'], filtered_df['prediction'])
    ax.set_xlabel('Trip Distance')
    ax.set_ylabel('Predicted Trip Duration (minutes)')
    st.pyplot(fig)

# Function for the Taxi Trip Duration Prediction App
def taxi_trip_duration_prediction_app(df, lookup_df):
    st.markdown("<h2 class='title'>Taxi Trip Duration Prediction App</h2>", unsafe_allow_html=True)
    merged_data = df.merge(lookup_df, left_on='PULocationID', right_on='LocationID', how='left', suffixes=('_PU', '_DO'))
    merged_data = merged_data.merge(lookup_df, left_on='DOLocationID', right_on='LocationID', how='left', suffixes=('_PU', '_DO'))

    default_pu_location = 'Bay Ridge'
    default_do_location = 'JFK Airport'

    pu_location = st.selectbox('Select Pickup Location', merged_data['Zone_PU'].unique(),
                               index=merged_data['Zone_PU'].unique().tolist().index(default_pu_location) if
                               default_pu_location in merged_data['Zone_PU'].unique() else 0)

    do_location = st.selectbox('Select Drop-off Location', merged_data['Zone_DO'].unique(),
                               index=merged_data['Zone_DO'].unique().tolist().index(default_do_location) if
                               default_do_location in merged_data['Zone_DO'].unique() else 0)

    if pu_location == do_location:
        st.warning('Please select different pickup and drop-off locations.')
    else:
        filtered_data = merged_data[(merged_data['Zone_PU'] == pu_location) & (merged_data['Zone_DO'] == do_location)]

        if not filtered_data.empty:
            predicted_duration_mean = filtered_data['prediction'].mean()
            st.success(f'Predicted Trip Duration: {predicted_duration_mean:.2f} minutes')
        else:
            st.warning('No prediction available for the selected criteria.')

# Main function
def main():
    st.markdown("<h1 class='title'>Trip Duration Prediction Dashboard</h1>", unsafe_allow_html=True)

    trip_duration_prediction_file = 'data/predictedData/trip_duration_pred.csv'  # Update with the correct file path
    lookup_table = 'data/dataFiles/taxi+_zone_lookup.csv'
    df_trip_duration = pd.read_csv(trip_duration_prediction_file)
    lookup_df = pd.read_csv(lookup_table)

    taxi_trip_duration_prediction_app(df_trip_duration, lookup_df)
    plot_heatmap_duration(df_trip_duration, lookup_df)
    plot_scatter_duration(df_trip_duration)

if __name__ == "__main__":
    main()
