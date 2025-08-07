import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import os

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

# Sample data (to be replaced with actual data loading)
@st.cache_data
def load_sample_data():
    # This is sample data - will be replaced with actual data loading
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='M')
    data = []
    
    for date in dates:
        for vehicle_type in ['2W', '3W', '4W']:
            for manufacturer in ['Hero', 'Honda', 'Maruti', 'Tata']:
                data.append({
                    'date': date,
                    'vehicle_type': vehicle_type,
                    'manufacturer': manufacturer,
                    'registrations': int(1000 * (1 + 0.1 * (vehicle_type == '2W') - 0.05 * (vehicle_type == '3W') + 0.2 * (date.month / 12)))
                })
    
    return pd.DataFrame(data)

# Load data
df = load_sample_data()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    # Initialize session state for date range if not exists
    if 'start_date' not in st.session_state:
        st.session_state.start_date = date.today() - timedelta(days=90)
    if 'end_date' not in st.session_state:
        st.session_state.end_date = date.today()
    
    today = date.today()
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
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

# Ensure dates are datetime objects
if not isinstance(start_date, datetime):
    start_date = datetime.combine(start_date, datetime.min.time())
if not isinstance(end_date, datetime):
    end_date = datetime.combine(end_date, datetime.max.time())

# Apply date filtering
filtered_df = df[
    (df['date'] >= start_date) & 
    (df['date'] <= end_date)
]

if selected_vehicle_type != 'All':
    filtered_df = filtered_df[filtered_df['vehicle_type'] == selected_vehicle_type]

if selected_manufacturer != 'All':
    filtered_df = filtered_df[filtered_df['manufacturer'] == selected_manufacturer]

# Calculate metrics
total_registrations = int(filtered_df['registrations'].sum())

# Calculate YoY and QoQ growth (sample calculation)
def calculate_growth(df, period):
    if period == 'yoy':
        current_year = end_date.year
        previous_year = current_year - 1
        current = df[df['date'].dt.year == current_year]['registrations'].sum()
        previous = df[df['date'].dt.year == previous_year]['registrations'].sum()
    else:  # qoq
        current_quarter = (end_date.month - 1) // 3 + 1
        previous_quarter = current_quarter - 1 if current_quarter > 1 else 4
        current = df[df['date'].dt.quarter == current_quarter]['registrations'].sum()
        previous = df[df['date'].dt.quarter == previous_quarter]['registrations'].sum()
    
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100

yoy_growth = calculate_growth(filtered_df, 'yoy')
qoq_growth = calculate_growth(filtered_df, 'qoq')

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Registrations", f"{total_registrations:,}")
with col2:
    st.metric("YoY Growth", f"{yoy_growth:+.1f}%")
with col3:
    st.metric("QoQ Growth", f"{qoq_growth:+.1f}%")

# Time series chart
if not filtered_df.empty:
    # Aggregate data by date for the chart
    time_series = filtered_df.groupby('date')['registrations'].sum().reset_index()
    
    fig = px.line(
        time_series, 
        x='date', 
        y='registrations',
        title=f"Vehicle Registrations ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})",
        labels={'date': 'Date', 'registrations': 'Number of Registrations'},
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# Data table with registrations by vehicle type and manufacturer
if not filtered_df.empty:
    st.subheader("Detailed Data")
    
    # Pivot table for better visualization
    pivot_df = filtered_df.pivot_table(
        index=['vehicle_type', 'manufacturer'],
        values='registrations',
        aggfunc='sum'
    ).reset_index()
    
    st.dataframe(
        pivot_df.sort_values('registrations', ascending=False),
        column_config={
            "vehicle_type": "Vehicle Type",
            "manufacturer": "Manufacturer",
            "registrations": st.column_config.NumberColumn("Registrations", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )

# Add a placeholder for future data source information
with st.expander("About the Data"):
    st.write("""
    This dashboard displays vehicle registration data from the Vahan Dashboard.
    
    **Data Source:** [Vahan Dashboard](https://vahan.parivahan.gov.in/vahan4dashboard/)
    
    Note: Currently showing sample data. The actual data collection module will be implemented next.
    """)
