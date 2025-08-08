import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Vehicle Registration Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stDateInput, .stSelectbox, .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🚗 Vehicle Registration Dashboard")
st.markdown("""
    Analyze vehicle registration data with year-over-year and quarter-over-quarter growth metrics.
    Filter by date range, vehicle type, and manufacturer.
""")

# Create necessary directories
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_sample_data():
    """Generate sample vehicle registration data with realistic patterns.
    
    Returns:
        pd.DataFrame: Sample vehicle registration data
    """
    try:
        # Generate monthly data for the past 3 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*3)  # 3 years of data
        dates = pd.date_range(start=start_date, end=end_date, freq='M')
        
        if len(dates) == 0:
            # Fallback to a fixed range if no dates generated
            dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='M')
        
        data = []
        vehicle_types = ['2W', '3W', '4W']
        manufacturers = ['Hero', 'Honda', 'Maruti', 'Tata', 'Bajaj', 'TVS', 'Yamaha', 'KTM']
        
        for date in dates:
            for vehicle_type in vehicle_types:
                for manufacturer in manufacturers[:4]:  # Limit to first 4 manufacturers for each type
                    # Base value with some randomness
                    base = 1000
                    
                    # Adjust by vehicle type
                    if vehicle_type == '2W':
                        base *= 1.5  # More 2-wheelers
                        if manufacturer in ['Hero', 'Honda', 'Bajaj', 'TVS']:
                            base *= 1.2  # Popular 2W manufacturers
                    elif vehicle_type == '3W':
                        base *= 0.6  # Fewer 3-wheelers
                        if manufacturer in ['Bajaj', 'TVS']:
                            base *= 1.5  # Popular 3W manufacturers
                    else:  # 4W
                        base *= 1.0
                        if manufacturer in ['Maruti', 'Tata', 'Honda']:
                            base *= 1.3  # Popular 4W manufacturers
                    
                    # Add seasonality (higher in certain months)
                    month_factor = 1.0 + 0.3 * (date.month % 3) / 3  # Varies by quarter
                    
                    # Add some randomness
                    random_factor = 0.9 + 0.2 * (hash(f"{date}{vehicle_type}{manufacturer}") % 10) / 10
                    
                    # Calculate final registration count
                    registrations = int(base * month_factor * random_factor)
                    
                    # Ensure minimum registrations
                    registrations = max(50, registrations)
                    
                    data.append({
                        'date': date,
                        'vehicle_type': vehicle_type,
                        'manufacturer': manufacturer,
                        'registrations': registrations
                    })
        
        df = pd.DataFrame(data)
        
        # Ensure date is in datetime format
        df['date'] = pd.to_datetime(df['date'])
        
        logger.info(f"Generated sample data with {len(df)} rows from {df['date'].min()} to {df['date'].max()}")
        return df
        
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        # Return a small sample dataframe with expected columns
        return pd.DataFrame({
            'date': [datetime.now()],
            'vehicle_type': ['4W'],
            'manufacturer': ['Sample'],
            'registrations': [1000]
        })

# Load data
df = load_sample_data()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
        # Get date range from data or use defaults
    today = datetime.now().date()
    default_start_date = today - timedelta(days=365)  # Default to 1 year of data
    
    # Initialize session state for date range if not exists
    if 'start_date' not in st.session_state:
        st.session_state.start_date = default_start_date
    if 'end_date' not in st.session_state:
        st.session_state.end_date = today
    
    # Ensure we have valid date ranges from the data
    if not df.empty and 'date' in df.columns:
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df['date']):
                df['date'] = pd.to_datetime(df['date'])
                
            # Get min and max dates from data
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            # Log the date range for debugging
            logger.info(f"Data date range: {min_date} to {max_date}")
            
            # If session dates are outside data range, adjust them
            if st.session_state.start_date < min_date:
                st.session_state.start_date = min_date
                logger.info(f"Adjusted start_date to {min_date}")
                
            if st.session_state.end_date > max_date:
                st.session_state.end_date = max_date
                logger.info(f"Adjusted end_date to {max_date}")
                
        except Exception as e:
            logger.error(f"Error processing date ranges: {str(e)}")
            min_date = default_start_date
            max_date = today
    else:
        # Fallback to reasonable defaults if no valid dates in data
        min_date = date(2022, 1, 1)
        max_date = today
        logger.warning("No valid date column found in data, using default date range")
    
    # Quick date range buttons
    st.write("Quick select:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("YTD"):
            st.session_state.start_date = date(today.year, 1, 1)
            st.session_state.end_date = today
    with col2:
        if st.button("Last 3M"):
            st.session_state.start_date = today - timedelta(days=90)
            st.session_state.end_date = today
    with col3:
        if st.button("Last Year"):
            st.session_state.start_date = date(today.year - 1, 1, 1)
            st.session_state.end_date = date(today.year - 1, 12, 31)
    
    # Date range inputs
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            value=st.session_state.start_date,
            min_value=min_date,
            max_value=st.session_state.end_date,
            key='start_date_input'
        )
    with col2:
        end_date = st.date_input(
            "End date",
            value=st.session_state.end_date,
            min_value=st.session_state.start_date,
            max_value=today,
            key='end_date_input'
        )
    
    # Update session state if dates are changed manually
    if start_date != st.session_state.start_date:
        st.session_state.start_date = start_date
    if end_date != st.session_state.end_date:
        st.session_state.end_date = end_date
    
    # Use session state dates for consistency
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    
    # Vehicle type filter
    vehicle_types = ['All'] + sorted(df['vehicle_type'].unique().tolist())
    selected_vehicle_type = st.selectbox("Vehicle Type", vehicle_types, index=0)
    
    # Manufacturer filter
    manufacturers = ['All'] + sorted(df['manufacturer'].unique().tolist())
    selected_manufacturer = st.selectbox("Manufacturer", manufacturers, index=0)

# Debug: Log the raw data info
logger.info(f"Raw data info: {df.info() if not df.empty else 'Empty DataFrame'}")
logger.info(f"Date range in data: {df['date'].min() if not df.empty else 'N/A'} to {df['date'].max() if not df.empty else 'N/A'}")

# Ensure we have valid data to work with
if df.empty or 'date' not in df.columns:
    st.error("No data available. Please check the data source.")
    st.stop()

# Ensure dates are datetime objects
if not isinstance(start_date, datetime):
    start_date = datetime.combine(start_date, datetime.min.time())
if not isinstance(end_date, datetime):
    end_date = datetime.combine(end_date, datetime.max.time())

# Make sure end of day is included
end_date = end_date.replace(hour=23, minute=59, second=59)

# Apply date filtering with error handling
try:
    # Create a copy to avoid SettingWithCopyWarning
    filtered_df = df.copy()
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(filtered_df['date']):
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    
    # Debug: Log the date range being filtered
    logger.info(f"Filtering data from {start_date} to {end_date}")
    
    # Apply date filter first (most common filter)
    date_mask = (filtered_df['date'].dt.date >= start_date.date()) & \
                (filtered_df['date'].dt.date <= end_date.date())
    
    # Debug: Count before and after date filter
    logger.info(f"Records before date filter: {len(filtered_df)}")
    filtered_df = filtered_df[date_mask].copy()
    logger.info(f"Records after date filter: {len(filtered_df)}")
    
    # Apply vehicle type filter if specified
    if selected_vehicle_type != 'All':
        logger.info(f"Filtering for vehicle type: {selected_vehicle_type}")
        vehicle_mask = filtered_df['vehicle_type'] == selected_vehicle_type
        logger.info(f"Records before vehicle filter: {len(filtered_df)}")
        filtered_df = filtered_df[vehicle_mask].copy()
        logger.info(f"Records after vehicle filter: {len(filtered_df)}")
    
    # Apply manufacturer filter if specified
    if selected_manufacturer != 'All':
        logger.info(f"Filtering for manufacturer: {selected_manufacturer}")
        mfg_mask = filtered_df['manufacturer'] == selected_manufacturer
        logger.info(f"Records before manufacturer filter: {len(filtered_df)}")
        filtered_df = filtered_df[mfg_mask].copy()
        logger.info(f"Records after manufacturer filter: {len(filtered_df)}")
    
    # If no data after filtering, show a helpful message
    if filtered_df.empty:
        st.warning("""
        No data available with the current filters. Try:
        - Expanding your date range
        - Selecting a different vehicle type
        - Choosing a different manufacturer
        - Or checking the data source
        """)
        
        # Show sample of available data
        st.info("Sample of available data:")
        st.dataframe(df.head())
        st.stop()
        
except Exception as e:
    logger.error(f"Error filtering data: {str(e)}", exc_info=True)
    st.error(f"An error occurred while filtering the data: {str(e)}")
    st.stop()

# Calculate metrics with error handling
try:
    total_registrations = int(filtered_df['registrations'].sum())
    
    def calculate_growth(df, period):
        """Calculate year-over-year or quarter-over-quarter growth.
        
        Args:
            df (pd.DataFrame): Filtered dataframe
            period (str): 'yoy' for year-over-year, 'qoq' for quarter-over-quarter
            
        Returns:
            float: Growth percentage
        """
        try:
            if df.empty or 'date' not in df.columns or 'registrations' not in df.columns:
                return 0.0
                
            if period == 'yoy':
                current_year = end_date.year
                previous_year = current_year - 1
                
                # Get data for current and previous year
                current_data = df[df['date'].dt.year == current_year]
                previous_data = df[df['date'].dt.year == previous_year]
                
                # If no data for previous year, return 0
                if previous_data.empty:
                    return 0.0
                    
                # Sum registrations for the period
                current = current_data['registrations'].sum()
                previous = previous_data['registrations'].sum()
                
            else:  # qoq
                current_quarter = (end_date.month - 1) // 3 + 1
                current_year = end_date.year
                
                # Handle year boundary for Q1
                if current_quarter == 1:
                    previous_quarter = 4
                    previous_year = current_year - 1
                else:
                    previous_quarter = current_quarter - 1
                    previous_year = current_year
                
                # Get data for current and previous quarter
                current_data = df[
                    (df['date'].dt.quarter == current_quarter) & 
                    (df['date'].dt.year == current_year)
                ]
                
                previous_data = df[
                    (df['date'].dt.quarter == previous_quarter) & 
                    (df['date'].dt.year == previous_year)
                ]
                
                # If no data for previous quarter, return 0
                if previous_data.empty:
                    return 0.0
                    
                current = current_data['registrations'].sum()
                previous = previous_data['registrations'].sum()
            
            # Calculate growth rate
            if previous == 0:
                return 0.0
                
            growth = ((current - previous) / previous) * 100
            return round(growth, 1)  # Round to 1 decimal place
            
        except Exception as e:
            logger.error(f"Error calculating {period} growth: {str(e)}")
            return 0.0
    
    # Calculate growth metrics
    yoy_growth = calculate_growth(filtered_df, 'yoy')
    qoq_growth = calculate_growth(filtered_df, 'qoq')
    
except Exception as e:
    logger.error(f"Error calculating metrics: {str(e)}")
    st.error("An error occurred while calculating metrics.")
    total_registrations = 0
    yoy_growth = 0.0
    qoq_growth = 0.0

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Registrations", f"{total_registrations:,}")
with col2:
    st.metric("YoY Growth", f"{yoy_growth:+.1f}%")
with col3:
    st.metric("QoQ Growth", f"{qoq_growth:+.1f}%")

# Time series chart
try:
    # Ensure we have data to plot
    if filtered_df.empty or 'date' not in filtered_df.columns or 'registrations' not in filtered_df.columns:
        st.warning("Insufficient data to generate time series chart.")
    else:
        # Make a copy to avoid SettingWithCopyWarning
        plot_df = filtered_df.copy()
        
        # Ensure date is datetime
        if not pd.api.types.is_datetime64_any_dtype(plot_df['date']):
            plot_df['date'] = pd.to_datetime(plot_df['date'])
        
        # Aggregate data by date for the chart
        time_series = plot_df.groupby('date')['registrations'].sum().reset_index()
        
        # Create the figure
        fig = px.line(
            time_series, 
            x='date', 
            y='registrations',
            title=f"Vehicle Registrations ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})",
            labels={'date': 'Date', 'registrations': 'Number of Registrations'},
            height=400
        )
        
        # Update layout for better readability
        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Registrations",
            hovermode='x unified',
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Add range slider
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
except Exception as e:
    logger.error(f"Error generating time series chart: {str(e)}")
    st.error("An error occurred while generating the time series chart.")

# Data table with registrations by vehicle type and manufacturer
try:
    if filtered_df.empty or 'vehicle_type' not in filtered_df.columns or 'manufacturer' not in filtered_df.columns:
        st.warning("Insufficient data to display detailed table.")
    else:
        st.subheader("Detailed Data")
        
        # Make a copy to avoid SettingWithCopyWarning
        table_df = filtered_df.copy()
        
        # Ensure numeric values
        if not pd.api.types.is_numeric_dtype(table_df['registrations']):
            table_df['registrations'] = pd.to_numeric(table_df['registrations'], errors='coerce')
        
        # Pivot table for better visualization
        pivot_df = table_df.pivot_table(
            index=['vehicle_type', 'manufacturer'],
            values='registrations',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Sort by registrations in descending order
        pivot_df = pivot_df.sort_values('registrations', ascending=False)
        
        # Display the table with some styling
        st.dataframe(
            pivot_df,
            column_config={
                "vehicle_type": "Vehicle Type",
                "manufacturer": "Manufacturer",
                "registrations": st.column_config.NumberColumn(
                    "Registrations", 
                    format="%d",
                    help="Total number of vehicle registrations"
                )
            },
            hide_index=True,
            use_container_width=True,
            height=min(400, 60 + len(pivot_df) * 35)  # Dynamic height based on rows
        )
        
        # Add download button for the data
        csv = pivot_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"vehicle_registrations_{start_date.date()}_to_{end_date.date()}.csv",
            mime="text/csv",
            help="Download the current view as a CSV file"
        )
        
except Exception as e:
    logger.error(f"Error generating data table: {str(e)}")
    st.error("An error occurred while generating the data table.")

# Add a placeholder for future data source information
with st.expander("About the Data"):
    st.write("""
    This dashboard displays vehicle registration data from the Vahan Dashboard.
    
    **Data Source:** [Vahan Dashboard](https://vahan.parivahan.gov.in/vahan4dashboard/)
    
    Note: Currently showing sample data. The actual data collection module will be implemented next.
    """)
