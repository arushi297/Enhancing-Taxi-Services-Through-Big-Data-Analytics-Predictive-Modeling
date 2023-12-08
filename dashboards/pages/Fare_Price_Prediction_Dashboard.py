import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Define the trip distance threshold
trip_distance_threshold = 0.2

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

# Function to plot interactive heatmap
def plot_heatmap(df, lookup_df):
    st.markdown("<h2 class='title'>Predicted Fare for Pickup and Dropoff Borough Location</h2>", unsafe_allow_html=True)
    # Merge with lookup table to get Borough for PU and DO LocationID
    df_merged = pd.merge(df, lookup_df[['LocationID', 'Borough']], left_on='PULocationID', right_on='LocationID', how='left')
    df_merged.rename(columns={'Borough': 'PUBorough'}, inplace=True)
    df_merged = pd.merge(df_merged, lookup_df[['LocationID', 'Borough']], left_on='DOLocationID', right_on='LocationID', how='left')
    df_merged.rename(columns={'Borough': 'DOBorough'}, inplace=True)

    # Filter out rows with small trip distances and specific days
    df_filtered = df_merged[
        (df_merged['trip_distance'] > trip_distance_threshold) &
        ((df_merged['day_of_the_month'] == 29) | (df_merged['day_of_the_month'] == 30))
    ]

    # Group by PU and DO Borough and calculate mean of fare prediction
    grouped_df = df_filtered.groupby(['PUBorough', 'DOBorough']).mean().reset_index()

    # Create a heatmap using Plotly
    fig = go.Figure(go.Heatmap(
        z=grouped_df['prediction'],
        x=grouped_df['DOBorough'],
        y=grouped_df['PUBorough'],
        colorscale='YlGnBu',
        colorbar=dict(title='Mean Prediction of Fare')
    ))

    # Customize layout
    fig.update_layout(
        title='Interactive Heatmap of Mean Fare Predictions',
        xaxis=dict(title='Drop-off Borough'),
        yaxis=dict(title='Pick-up Borough')
    )

    # Show the interactive heatmap
    st.plotly_chart(fig)
    st.write("Darker heatmap color represents a higher fare price")


# Function to plot scatter plot
def plot_scatter(df):
    filtered_df = df[(df['day_of_the_month'].isin([29, 30])) & (df['trip_distance'] > trip_distance_threshold) & (df['trip_distance'] <= 1000)]

    st.markdown("<h2 class='title'>Taxi Predicted Fare vs Trip Distance</h2>", unsafe_allow_html=True)

    # Scatter plot
    st.write("**Trip Distance vs Predicted Fare**")
    fig, ax = plt.subplots()
    ax.scatter(filtered_df['trip_distance'], filtered_df['prediction'])
    ax.set_xlabel('Trip Distance')
    ax.set_ylabel('Predicted Fare Price')
    st.pyplot(fig)


# Function for the Taxi Fare Prediction App
def taxi_fare_prediction_app(df, lookup_df):
    st.markdown("<h2 class='title'>Taxi Fare Price Prediction App</h2>", unsafe_allow_html=True)
    merged_data = df.merge(lookup_df, left_on='PULocationID', right_on='LocationID', how='left', suffixes=('_PU', '_DO'))
    merged_data = merged_data.merge(lookup_df, left_on='DOLocationID', right_on='LocationID', how='left', suffixes=('_PU', '_DO'))

    default_pu_location = 'Bay Ridge'
    default_do_location = 'JFK Airport'
    default_selected_hour = 17

    pu_location = st.selectbox('Select Pickup Location', merged_data['Zone_PU'].unique(),
                               index=merged_data['Zone_PU'].unique().tolist().index(default_pu_location) if
                               default_pu_location in merged_data['Zone_PU'].unique() else 0)

    do_location = st.selectbox('Select Drop-off Location', merged_data['Zone_DO'].unique(),
                               index=merged_data['Zone_DO'].unique().tolist().index(default_do_location) if
                               default_do_location in merged_data['Zone_DO'].unique() else 0)

    selected_hour = st.slider('Select Hour of Day', 0, 23, value=default_selected_hour, step=1)

    if pu_location == do_location:
        st.warning('Please select different pickup and drop-off locations.')
    else:
        filtered_data = merged_data[(merged_data['Zone_PU'] == pu_location) & (merged_data['Zone_DO'] == do_location) & (
                    merged_data['hour_of_day'] == selected_hour)]

        if not filtered_data.empty:
            predicted_fare_mean = filtered_data['prediction'].mean()
            st.success(f'Predicted Fare: ${predicted_fare_mean:.2f}')
        else:
            st.warning('No prediction available for the selected criteria.')


def main():
    st.markdown("<h1 class='title'>Fare Price Prediction Dashboard</h1>", unsafe_allow_html=True)

    taxi_fare_prediction = 'data/predictedData/fare_predictions.csv'
    lookup_table = 'data/dataFiles/taxi+_zone_lookup.csv'
    df = pd.read_csv(taxi_fare_prediction)
    lookup_df = pd.read_csv(lookup_table)

    taxi_fare_prediction_app(df, lookup_df)
    plot_heatmap(df, lookup_df)
    plot_scatter(df)


if __name__ == "__main__":
    main()
