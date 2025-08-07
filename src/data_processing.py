"""
Data processing module for cleaning and analyzing vehicle registration data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

class DataProcessor:
    """Class for processing and analyzing vehicle registration data."""
    
    def __init__(self, df: pd.DataFrame = None):
        """Initialize the data processor with a DataFrame.
        
        Args:
            df: Optional DataFrame to process
        """
        self.df = df
        self.processed_data = {}
    
    def load_data(self, filepath: str) -> bool:
        """Load data from a CSV file.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            self.df = pd.read_csv(filepath, parse_dates=['date'], infer_datetime_format=True)
            logger.info(f"Successfully loaded data from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading data from {filepath}: {e}")
            return False
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and preprocess the data.
        
        Returns:
            Cleaned DataFrame
        """
        if self.df is None or self.df.empty:
            logger.warning("No data to clean")
            return None
        
        # Make a copy to avoid modifying the original
        df = self.df.copy()
        
        # Convert date to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Drop rows with invalid dates
        original_count = len(df)
        df = df.dropna(subset=['date'])
        if len(df) < original_count:
            logger.warning(f"Dropped {original_count - len(df)} rows with invalid dates")
        
        # Ensure numeric columns are of correct type
        numeric_cols = ['registrations']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill missing values
        df['registrations'] = df['registrations'].fillna(0).astype(int)
        
        # Add derived date columns
        df['year'] = df['date'].dt.year
        df['quarter'] = df['date'].dt.quarter
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['year_quarter'] = df['year'].astype(str) + ' Q' + df['quarter'].astype(str)
        
        # Sort by date
        df = df.sort_values('date')
        
        self.df = df
        return df
    
    def calculate_metrics(self) -> Dict:
        """Calculate key metrics from the data.
        
        Returns:
            Dictionary containing calculated metrics
        """
        if self.df is None or self.df.empty:
            return {}
        
        metrics = {}
        
        # Total registrations
        metrics['total_registrations'] = int(self.df['registrations'].sum())
        
        # Get the date range
        min_date = self.df['date'].min()
        max_date = self.df['date'].max()
        metrics['date_range'] = {
            'start': min_date.strftime('%Y-%m-%d'),
            'end': max_date.strftime('%Y-%m-%d')
        }
        
        # Calculate YoY growth
        if len(self.df['year'].unique()) > 1:
            current_year = max(self.df['year'])
            previous_year = current_year - 1
            
            current_year_data = self.df[self.df['year'] == current_year]
            previous_year_data = self.df[self.df['year'] == previous_year]
            
            if not previous_year_data.empty:
                current_total = current_year_data['registrations'].sum()
                previous_total = previous_year_data['registrations'].sum()
                
                if previous_total > 0:
                    yoy_growth = ((current_total - previous_total) / previous_total) * 100
                    metrics['yoy_growth'] = round(yoy_growth, 2)
        
        # Calculate QoQ growth
        if len(self.df['year_quarter'].unique()) > 1:
            quarters = sorted(self.df['year_quarter'].unique())
            current_q = quarters[-1]
            
            # Find previous quarter
            if len(quarters) > 1:
                prev_q = quarters[-2]
                current_q_data = self.df[self.df['year_quarter'] == current_q]
                prev_q_data = self.df[self.df['year_quarter'] == prev_q]
                
                current_total = current_q_data['registrations'].sum()
                prev_total = prev_q_data['registrations'].sum()
                
                if prev_total > 0:
                    qoq_growth = ((current_total - prev_total) / prev_total) * 100
                    metrics['qoq_growth'] = round(qoq_growth, 2)
        
        # Top manufacturers
        if 'manufacturer' in self.df.columns:
            manufacturer_totals = (
                self.df.groupby('manufacturer')['registrations']
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            metrics['top_manufacturers'] = manufacturer_totals.to_dict()
        
        # Vehicle type distribution
        if 'vehicle_type' in self.df.columns:
            type_dist = (
                self.df.groupby('vehicle_type')['registrations']
                .sum()
                .sort_values(ascending=False)
            )
            metrics['vehicle_type_distribution'] = type_dist.to_dict()
        
        self.processed_data['metrics'] = metrics
        return metrics
    
    def get_time_series(self, freq: str = 'M') -> pd.DataFrame:
        """Get time series data at the specified frequency.
        
        Args:
            freq: Frequency for resampling ('M' for monthly, 'Q' for quarterly)
            
        Returns:
            DataFrame with time series data
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        # Resample to the specified frequency
        time_series = (
            self.df.set_index('date')
            .resample(freq)['registrations']
            .sum()
            .reset_index()
        )
        
        # Add year and month/quarter columns
        time_series['year'] = time_series['date'].dt.year
        
        if freq == 'M':
            time_series['month'] = time_series['date'].dt.month
            time_series['month_name'] = time_series['date'].dt.strftime('%b')
        elif freq == 'Q':
            time_series['quarter'] = time_series['date'].dt.quarter
            time_series['year_quarter'] = (
                time_series['year'].astype(str) + ' Q' + 
                time_series['quarter'].astype(str)
            )
        
        return time_series
    
    def get_breakdown(self, by: str = 'vehicle_type') -> pd.DataFrame:
        """Get data broken down by the specified column.
        
        Args:
            by: Column to group by ('vehicle_type' or 'manufacturer')
            
        Returns:
            DataFrame with the breakdown
        """
        if self.df is None or self.df.empty or by not in self.df.columns:
            return pd.DataFrame()
        
        breakdown = (
            self.df.groupby(by)['registrations']
            .sum()
            .reset_index()
            .sort_values('registrations', ascending=False)
        )
        
        return breakdown
    
    def get_trends(self, group_by: str = 'vehicle_type') -> Dict[str, pd.DataFrame]:
        """Get trend data for different groups over time.
        
        Args:
            group_by: Column to group by ('vehicle_type' or 'manufacturer')
            
        Returns:
            Dictionary with group names as keys and DataFrames as values
        """
        if self.df is None or self.df.empty or group_by not in self.df.columns:
            return {}
        
        # Pivot the data to get time series for each group
        pivot_df = (
            self.df.groupby(['date', group_by])['registrations']
            .sum()
            .unstack()
            .fillna(0)
        )
        
        # Convert to dictionary of DataFrames
        trends = {}
        for col in pivot_df.columns:
            trends[col] = pivot_df[col].reset_index()
        
        return trends

def load_processed_data(filename: str = 'processed_data.parquet') -> Optional[Dict]:
    """Load processed data from disk.
    
    Args:
        filename: Name of the file to load
        
    Returns:
        Dictionary containing the processed data or None if failed
    """
    filepath = PROCESSED_DIR / filename
    
    try:
        if filepath.suffix == '.parquet':
            df = pd.read_parquet(filepath)
        else:  # Assume CSV
            df = pd.read_csv(filepath, parse_dates=['date'])
        
        processor = DataProcessor(df)
        processor.clean_data()
        metrics = processor.calculate_metrics()
        
        return {
            'data': processor.df,
            'metrics': metrics,
            'time_series': processor.get_time_series('M'),
            'quarterly_series': processor.get_time_series('Q'),
            'vehicle_type_breakdown': processor.get_breakdown('vehicle_type'),
            'manufacturer_breakdown': processor.get_breakdown('manufacturer'),
            'trends': processor.get_trends('vehicle_type')
        }
    except Exception as e:
        logger.error(f"Error loading processed data: {e}")
        return None

def save_processed_data(data: Dict, filename: str = 'processed_data.parquet') -> bool:
    """Save processed data to disk.
    
    Args:
        data: Dictionary containing the processed data
        filename: Name of the file to save
        
    Returns:
        bool: True if saving was successful, False otherwise
    """
    if not data or 'data' not in data:
        logger.error("No data to save")
        return False
    
    filepath = PROCESSED_DIR / filename
    
    try:
        if filepath.suffix == '.parquet':
            data['data'].to_parquet(filepath, index=False)
        else:  # Save as CSV
            data['data'].to_csv(filepath, index=False)
        
        logger.info(f"Processed data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    processor = DataProcessor()
    
    # Load sample data (replace with actual data loading)
    from data_collection import VahanDataCollector
    
    collector = VahanDataCollector()
    try:
        # Get data for the last 12 months
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - pd.DateOffset(months=12)).strftime("%Y-%m-%d")
        
        df = collector.fetch_data(start_date, end_date)
        if df is not None:
            processor = DataProcessor(df)
            cleaned_df = processor.clean_data()
            metrics = processor.calculate_metrics()
            
            print(f"Total registrations: {metrics.get('total_registrations'):,}")
            print(f"YoY Growth: {metrics.get('yoy_growth', 'N/A')}%")
            print(f"QoQ Growth: {metrics.get('qoq_growth', 'N/A')}%")
            
            # Save processed data
            processed_data = {
                'data': cleaned_df,
                'metrics': metrics,
                'time_series': processor.get_time_series('M'),
                'quarterly_series': processor.get_time_series('Q'),
                'vehicle_type_breakdown': processor.get_breakdown('vehicle_type'),
                'manufacturer_breakdown': processor.get_breakdown('manufacturer'),
                'trends': processor.get_trends('vehicle_type')
            }
            
            save_processed_data(processed_data)
    finally:
        collector.close()
