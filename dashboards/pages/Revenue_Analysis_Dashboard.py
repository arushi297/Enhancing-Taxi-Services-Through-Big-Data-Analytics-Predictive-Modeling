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


# Define the function to get taxi revenues
def get_taxi_revenues(connection):
    # Execute SQL query for daily revenue
    daily_query = '''
        SELECT
            DATE(tpep_pickup_datetime) AS Date,
            SUM(total_amount) AS DailyRevenue
        FROM
            (
                SELECT
                    tpep_pickup_datetime,
                    total_amount
                FROM
                    yellow_tripdata
                WHERE
                    strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
                UNION ALL
                SELECT
                    lpep_pickup_datetime,
                    total_amount
                FROM
                    green_tripdata
                WHERE
                    strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
            ) AS combined_taxi
        GROUP BY
            Date
        ORDER BY
            Date;
    '''
    daily = pd.read_sql_query(daily_query, connection)

    # Execute SQL query for weekly revenue
    weekly_query = '''
        SELECT
            strftime('%Y-%m-%d', tpep_pickup_datetime, 'weekday 0', '-6 days') AS WeekStart,
            SUM(total_amount) AS WeeklyRevenue
        FROM
            (
                SELECT
                    tpep_pickup_datetime,
                    total_amount
                FROM
                    yellow_tripdata
                WHERE
                    strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
                UNION ALL
                SELECT
                    lpep_pickup_datetime,
                    total_amount
                FROM
                    green_tripdata
                WHERE
                    strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
            ) AS combined_taxi
        GROUP BY
            WeekStart
        ORDER BY
            WeekStart;
    '''
    weekly = pd.read_sql_query(weekly_query, connection)

    # Execute SQL query for monthly revenue
    monthly_query = '''
        SELECT
            strftime('%Y-%m', tpep_pickup_datetime) AS Month,
            SUM(total_amount) AS MonthlyRevenue
        FROM
            (
                SELECT
                    tpep_pickup_datetime,
                    total_amount
                FROM
                    yellow_tripdata
                WHERE
                    strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
                UNION ALL
                SELECT
                    lpep_pickup_datetime,
                    total_amount
                FROM
                    green_tripdata
                WHERE
                    strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
            ) AS combined_taxi
        GROUP BY
            Month
        ORDER BY
            Month;
    '''
    monthly = pd.read_sql_query(monthly_query, connection)

    # Main page
    st.markdown("<h2 class='title'>Daily, Weekly, and Monthly Revenue Trends</h2>", unsafe_allow_html=True)
    
    # Daily Revenue Trends
    st.subheader("Daily Revenue Trends:")
    st.dataframe(daily)
    st.markdown("""
    - The daily revenue trends show fluctuations throughout the month of September.
    - The highest daily revenue was observed on September 7th, amounting to "$3,835,893.89."
    - There are noticeable peaks and troughs in daily revenue, indicating potential patterns related to specific days of the week or events.
    """)

    fig_daily_hist = px.line(daily, x='Date', y='DailyRevenue', title='Daily Revenue Trends')
    st.plotly_chart(fig_daily_hist)

    # Weekly Revenue Trends
    st.subheader("Weekly Revenue Trends:")
    st.dataframe(weekly)
    st.markdown("""
    - Weekly revenue data reveals varying performance across different weeks in September.
    - Week starting on September 4th has the highest weekly revenue, totaling "$23,331,885.68."
    - The subsequent weeks also display substantial revenue, with the last week of September reaching "$19,976,939.08."
    """)

    # Create a line chart for weekly revenue trends
    fig_weekly_line = px.line(weekly, x='WeekStart', y='WeeklyRevenue', title='Weekly Revenue Trends')
    st.plotly_chart(fig_weekly_line)

    # Monthly Revenue
    st.subheader("Monthly Revenue:")
    st.dataframe(monthly)
    st.markdown("""
    - The total monthly revenue for September amounts to "$86,516,586.97."
    - The monthly revenue is a sum of daily revenues and reflects the overall financial performance of the taxi service for the entire month.
    """)

def get_revenue_vary(connection):
    revenue_by_location_query = '''
    SELECT
        tz.LocationID,
        tz.Borough,
        tz.Zone,
        SUM(total_amount) AS TotalRevenue
    FROM
        taxi_zone_lookup tz
    JOIN
        (
            SELECT
                PULocationID,
                total_amount
            FROM
                yellow_tripdata
            WHERE
                strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
            UNION ALL
            SELECT
                PULocationID,
                total_amount
            FROM
                green_tripdata
            WHERE
                strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
        ) AS combined_taxi
    ON
        tz.LocationID = combined_taxi.PULocationID
    GROUP BY
        tz.LocationID, tz.Borough, tz.Zone
    ORDER BY
        TotalRevenue DESC;
    '''

    R_location = pd.read_sql_query(revenue_by_location_query, connection)

    revenue_by_time_query = '''
        SELECT
            strftime('%H', pickup_datetime) AS HourOfDay,
            SUM(total_amount) AS TotalRevenue
        FROM
            (
                SELECT
                    tpep_pickup_datetime AS pickup_datetime,
                    total_amount
                FROM
                    yellow_tripdata
                WHERE
                    strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
                UNION ALL
                SELECT
                    lpep_pickup_datetime AS pickup_datetime,
                    total_amount
                FROM
                    green_tripdata
                WHERE
                    strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
            ) AS combined_taxi
        GROUP BY
            HourOfDay
        ORDER BY
            HourOfDay;
    '''


    R_time = pd.read_sql_query(revenue_by_time_query, connection)
    

    revenue_by_dayweek_query = '''
        SELECT
            strftime('%w', pickup_datetime) AS DayOfWeek,
            SUM(total_amount) AS TotalRevenue
        FROM
            (
                SELECT
                    tpep_pickup_datetime AS pickup_datetime,
                    total_amount
                FROM
                    yellow_tripdata
                WHERE
                    strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
                UNION ALL
                SELECT
                    lpep_pickup_datetime AS pickup_datetime,
                    total_amount
                FROM
                    green_tripdata
                WHERE
                    strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
            ) AS combined_taxi
        GROUP BY
            DayOfWeek
        ORDER BY
            DayOfWeek;
    '''

    R_day = pd.read_sql_query(revenue_by_dayweek_query, connection)
    
    st.markdown("<h2 class='title'>Revenue vary by Location, Time of day, and Day of the week</h2>", unsafe_allow_html=True)

    # Display bar chart for revenue by location
    st.subheader("Revenue by Location")
    st.write(
    "1. **Airport Dominance:** The highest revenue-generating location is the JFK airport in Queens, contributing approximately "
    f'"{R_location["TotalRevenue"].max():,.0f}". This emphasizes the significant impact of airport-related services '
    "on overall taxi revenue."
    )
    st.write(
    "2. **LaGuardia's Significant Role:** Another airport in Queens, contributing around "
    f'"{R_location.loc[1, "TotalRevenue"]:,.0f}", also plays a crucial role. While not as high as the first airport, '
    "its presence underscores the importance of multiple airports in shaping taxi revenue."
    )
    st.write(
    "3. **Diverse Manhattan Hotspots:** Several Manhattan locations showcase substantial revenue diversity. Hotspots like "
    f'Midtown Center and Upper East Side South collectively contribute millions, highlighting the borough\'s pivotal role '
    "in taxi services."
    )


    # Use the revenue_by_location DataFrame obtained from the function
    fig_location = px.bar(R_location, x='TotalRevenue', y='Zone', orientation='h', title='Revenue by Location')
    st.plotly_chart(fig_location)

    st.subheader("Revenue by Time of Day")

    st.write(
    "1. **Peak Hours Impact:** The hours between 17:00 (5 PM) and 19:00 (7 PM) demonstrate consistently high revenue, "
    f"with the highest revenue observed at 17:00, totaling '{R_time['TotalRevenue'].max():,.2f}'. "
    "This period likely represents peak demand hours."
    )
    st.write(
    "2. **Morning Rush:** The early morning hours, particularly around 08:00 and 09:00, also contribute significantly "
    f"to the total revenue, reaching '{R_time.loc[8:9, 'TotalRevenue'].sum():,.2f}'. This could be attributed "
    "to the morning rush hours."
    )
    st.write(
    "3. **Late Night Decrease:** Revenue starts to decrease after 21:00 (9 PM), reaching the lowest point at 23:00 "
    f"(11 PM) with total revenue of '{R_time.loc[23, 'TotalRevenue']:,.2f}'. Late-night demand appears to be lower."
    )

    
    # Revenue by Time of Day
    fig_time = px.line(R_time, x='HourOfDay', y='TotalRevenue', title='Revenue by Time of Day')
    st.plotly_chart(fig_time)

    

    st.subheader("Revenue by Day of the Week")
    

    # Display Revenue by Day of the Week
    day_of_week_mapping = {
    '0': 'Monday',
    '1': 'Tuesday',
    '2': 'Wednesday',
    '3': 'Thursday',
    '4': 'Friday',
    '5': 'Saturday',
    '6': 'Sunday'
    }

    R_day['DayOfWeek'] = R_day['DayOfWeek'].map(day_of_week_mapping)
    fig_day_week = px.bar(R_day, x='TotalRevenue', y='DayOfWeek', orientation='h', title='Revenue by Day of the Week', labels={'DayOfWeek': 'Day'})
    st.plotly_chart(fig_day_week)

    st.write(
    "1. **Midweek Surge:** The middle of the week, specifically Tuesday (Day 1), Wednesday (Day 2), and Thursday (Day 3), "
    f"shows a substantial increase in revenue, totaling around '{R_day.loc[1:3, 'TotalRevenue'].sum():,.2f}'. "
    "This suggests higher demand during midweek days."
    )
    st.write(
    "2. **Weekend Revenue:** Weekends, including Saturday (Day 5) and Sunday (Day 6), contribute significantly to the total revenue, "
    f"reaching approximately '{R_day.loc[5:6, 'TotalRevenue'].sum():,.2f}'. The weekend demand appears to be strong."
    )

def get_revenue_by_trip_type(connection):
    # Execute SQL query for airport and non-airport trips with RatecodeID IN (2, 3)
    revenue_by_trip_type_query = '''
    SELECT
        CASE
            WHEN RatecodeID IN (2, 3) THEN 'Airport'
            ELSE 'Non-Airport'
        END AS TripType,
        SUM(total_amount) AS TotalRevenue
    FROM
        (
            SELECT
                total_amount,
                RatecodeID
            FROM
                yellow_tripdata
            WHERE
                strftime('%Y-%m', tpep_pickup_datetime) = '2023-09'
                AND (RatecodeID IS NULL OR RatecodeID IN (2, 3))
            UNION ALL
            SELECT
                total_amount,
                RatecodeID
            FROM
                green_tripdata
            WHERE
                strftime('%Y-%m', lpep_pickup_datetime) = '2023-09'
                AND (RatecodeID IS NULL OR RatecodeID IN (2, 3))
        ) AS combined_taxi
    GROUP BY
        TripType
    ORDER BY
        TotalRevenue DESC;'''

    # Execute the query and load results into a DataFrame
    revenue_by_trip_type = pd.read_sql_query(revenue_by_trip_type_query, connection)

    # Streamlit Pie Chart
    
    st.markdown("<h2 class='title'>Revenue Comparison - Airport vs. Non-Airport Trips</h2>", unsafe_allow_html=True)

    st.markdown("""
1. **Airport Dominance:** The data reveals that trips to and from airports significantly contribute to the overall taxi service revenue. The "Airport" category, encompassing rides associated with airports, generates substantial revenue, amounting to approximately "$11,456,650."

2. **Non-Airport Revenue:** While airport trips dominate, non-airport trips also play a noteworthy role in contributing to taxi service revenue. The "Non-Airport" category, covering rides unrelated to airports, contributes a substantial amount, totaling around "$4,423,475."

3. **Revenue Disparity:** The revenue comparison highlights a significant disparity between airport and non-airport trips. Airport-related services contribute more than double the revenue compared to non-airport trips. This emphasizes the strategic importance of locations associated with airports in shaping the financial performance of the taxi service.
""")


    fig_pie = px.pie(
        revenue_by_trip_type,
        names='TripType',
        values='TotalRevenue',
        title='Revenue Distribution by Trip Type'
    )

    st.plotly_chart(fig_pie)




    

    


def main():

    st.markdown("<h1 class='title'>Revenue Analysis Dashboard</h1>", unsafe_allow_html=True)

    # Connect to the database
    connection = sqlite3.connect('nyc_taxi_database.db')

    # Call the plot function with the database connection
    get_taxi_revenues(connection)

    get_revenue_vary(connection)

    get_revenue_by_trip_type(connection)

    # Close the database connection
    connection.close()


if __name__ == "__main__":
    main()


