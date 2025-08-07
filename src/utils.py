"""
Utility functions and configurations for the Vehicle Registration Dashboard.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project directories
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
MODELS_DIR = ROOT_DIR / 'models'
REPORTS_DIR = ROOT_DIR / 'reports'

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration
def load_config(config_file: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from a YAML file.
    
    Args:
        config_file: Path to the config file (relative to project root)
        
    Returns:
        Dictionary containing the configuration
    """
    config_path = ROOT_DIR / config_file
    
    if not config_path.exists():
        logger.warning(f"Config file {config_path} not found. Using default configuration.")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config file {config_path}: {e}")
        return {}

# Data loading and saving
def save_json(data: Any, filepath: Union[str, Path], indent: int = 2) -> bool:
    """Save data to a JSON file.
    
    Args:
        data: Data to save (must be JSON-serializable)
        filepath: Path to save the file to
        indent: Indentation level for pretty-printing
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False

def load_json(filepath: Union[str, Path]) -> Optional[Dict]:
    """Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary with the loaded data or None if failed
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return None

# Date and time utilities
def parse_date_range(start_date: str, end_date: str, freq: str = 'D') -> List[str]:
    """Generate a list of dates between start_date and end_date.
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        freq: Frequency of dates ('D' for daily, 'M' for monthly, 'Q' for quarterly)
        
    Returns:
        List of date strings in 'YYYY-MM-DD' format
    """
    import pandas as pd
    
    try:
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        return [d.strftime('%Y-%m-%d') for d in dates]
    except Exception as e:
        logger.error(f"Error generating date range: {e}")
        return []

def get_quarter(date_str: str) -> str:
    """Get the quarter for a given date string.
    
    Args:
        date_str: Date in 'YYYY-MM-DD' format
        
    Returns:
        String in 'YYYY-Q1/Q2/Q3/Q4' format
    """
    from datetime import datetime
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        quarter = (date.month - 1) // 3 + 1
        return f"{date.year}-Q{quarter}"
    except Exception as e:
        logger.error(f"Error getting quarter for {date_str}: {e}")
        return ""

# Data validation
def validate_dataframe(df, required_columns: List[str] = None) -> bool:
    """Validate that a DataFrame has the required columns and is not empty.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        bool: True if valid, False otherwise
    """
    if df is None or df.empty:
        logger.warning("DataFrame is None or empty")
        return False
    
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
    
    return True

# Visualization utilities
def get_color_palette() -> Dict[str, str]:
    """Get a consistent color palette for visualizations.
    
    Returns:
        Dictionary mapping categories to colors
    """
    return {
        '2W': '#1f77b4',  # Blue
        '3W': '#ff7f0e',   # Orange
        '4W': '#2ca02c',   # Green
        'Hero': '#d62728', # Red
        'Honda': '#9467bd', # Purple
        'Maruti': '#8c564b', # Brown
        'Tata': '#e377c2',  # Pink
        'Bajaj': '#7f7f7f', # Gray
        'TVS': '#bcbd22',   # Olive
        'Yamaha': '#17becf', # Cyan
        'Mahindra': '#ff9896' # Light red
    }

# Logging utilities
def setup_logging(log_file: str = 'vahan_dashboard.log', log_level: str = 'INFO'):
    """Set up logging configuration.
    
    Args:
        log_file: Name of the log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_path = ROOT_DIR / 'logs' / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = log_levels.get(log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

# Configuration for the dashboard
def get_dashboard_config() -> Dict[str, Any]:
    """Get configuration for the Streamlit dashboard.
    
    Returns:
        Dictionary with dashboard configuration
    """
    return {
        'page_title': 'Vehicle Registration Dashboard',
        'page_icon': '🚗',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded',
        'menu_items': {
            'Get Help': 'https://vahan.parivahan.gov.in/vahan4dashboard/',
            'Report a bug': 'https://github.com/yourusername/vehicle-registration-dashboard/issues',
            'About': """
            # Vehicle Registration Dashboard
            
            This dashboard provides insights into vehicle registration data from the Vahan Dashboard.
            
            **Data Source:** [Vahan Dashboard](https://vahan.parivahan.gov.in/vahan4dashboard/)
            """
        },
        'theme': {
            'primaryColor': '#1f77b4',
            'backgroundColor': '#ffffff',
            'secondaryBackgroundColor': '#f0f2f6',
            'textColor': '#262730',
            'font': 'sans serif'
        }
    }

if __name__ == "__main__":
    # Example usage
    print(f"Project root directory: {ROOT_DIR}")
    
    # Example of using the date utilities
    dates = parse_date_range('2023-01-01', '2023-01-10')
    print(f"First 10 days of 2023: {dates[:10]}")
    
    # Example of getting a quarter
    print(f"Quarter for 2023-05-15: {get_quarter('2023-05-15')}")
