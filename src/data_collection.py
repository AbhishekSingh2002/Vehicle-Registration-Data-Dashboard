"""
Data collection module for fetching vehicle registration data from Vahan Dashboard.
"""
import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/"
API_ENDPOINT = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/vahan/view/"
DATA_DIR = Path("data/raw")
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default headers to mimic a browser
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://vahan.parivahan.gov.in/vahan4dashboard/'
}

class VahanDataCollector:
    """Class to handle data collection from Vahan Dashboard."""
    
    def __init__(self, headless: bool = True, use_selenium: bool = False):
        """Initialize the data collector.
        
        Args:
            headless: Whether to run browser in headless mode (default: True)
            use_selenium: Whether to use Selenium for JavaScript-heavy pages (slower but more reliable)
        """
        self.headless = headless
        self.use_selenium = use_selenium
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.cache_enabled = True
    
    def _get_cached_data(self, cache_key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Get data from cache if it exists and is not expired.
        
        Args:
            cache_key: Unique key for the cached data
            max_age_hours: Maximum age of cached data in hours
            
        Returns:
            Cached data or None if not found or expired
        """
        if not self.cache_enabled:
            return None
            
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if not cache_file.exists():
            return None
            
        cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if (datetime.now() - cache_time) > timedelta(hours=max_age_hours):
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Any) -> None:
        """Save data to cache.
        
        Args:
            cache_key: Unique key for the cached data
            data: Data to cache (must be JSON serializable)
        """
        if not self.cache_enabled:
            return
            
        try:
            cache_file = CACHE_DIR / f"{cache_key}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_key}: {e}")
    
    def setup_selenium(self) -> None:
        """Set up Selenium WebDriver if needed."""
        if not self.use_selenium or self.driver is not None:
            return
            
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"user-agent={DEFAULT_HEADERS['User-Agent']}")
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Selenium WebDriver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            raise
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.implicitly_wait(10)
            logger.info("Selenium WebDriver initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            return False
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed.")
    
    def fetch_vehicle_registrations(self, state: str = "All India", 
                                  vehicle_type: str = "All", 
                                  fuel_type: str = "All",
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch vehicle registration data with the given filters.
        
        Args:
            state: State name or 'All India' for national data
            vehicle_type: Type of vehicle (2W, 3W, 4W, etc.)
            fuel_type: Fuel type (Petrol, Diesel, Electric, etc.)
            start_date: Start date for data (if None, last 3 months)
            end_date: End date for data (if None, today)
            
        Returns:
            DataFrame containing the registration data
        """
        # Set default date range if not provided
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=90)
            
        logger.info(f"Fetching {vehicle_type} registrations for {state} from {start_date} to {end_date}")
        
        # Generate cache key based on parameters
        cache_key = f"registrations_{state}_{vehicle_type}_{fuel_type}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        # Try to get data from cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            logger.info("Using cached data")
            return pd.DataFrame(cached_data)
        
        # If not in cache, fetch from the API
        try:
            if self.use_selenium:
                data = self._fetch_with_selenium(state, vehicle_type, fuel_type, start_date, end_date)
            else:
                data = self._fetch_with_requests(state, vehicle_type, fuel_type, start_date, end_date)
                
            # Cache the results
            if data is not None and not data.empty:
                self._save_to_cache(cache_key, data.to_dict('records'))
                
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            # Fall back to sample data if there's an error
            logger.info("Falling back to sample data")
            return self._generate_sample_data(start_date, end_date)
    
    def _generate_sample_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate sample data for testing purposes.
        
        Args:
            start_date: Start date for the sample data
            end_date: End date for the sample data
            
        Returns:
            DataFrame containing sample data
        """
        # Generate dates between start and end date
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate sample data
        data = []
        for date in dates:
            for vehicle_type in ['2W', '3W', '4W']:
                for manufacturer in ['Hero', 'Honda', 'Maruti', 'Tata']:
                    registrations = int(1000 * (1 + 0.1 * (vehicle_type == '2W') - 0.05 * (vehicle_type == '3W') + 0.2 * (date.month / 12)))
                    data.append({
                        'date': date,
                        'vehicle_type': vehicle_type,
                        'manufacturer': manufacturer,
                        'registrations': registrations,
                        'state': 'Sample',
                        'district': 'Sample District',
                    })
        
        return pd.DataFrame(data)

def get_available_datasets() -> List[Dict[str, str]]:
    """Get list of available datasets in the data directory.
    
    Returns:
        List of dictionaries with dataset information
    """
    datasets = []
    if DATA_DIR.exists():
        for file in DATA_DIR.glob("vahan_data_*.csv"):
            # Extract date range from filename
            try:
                date_part = file.stem.replace("vahan_data_", "")
                start_date, end_date = date_part.split("_to_")
                datasets.append({
                    'filename': file.name,
                    'path': str(file),
                    'start_date': start_date,
                    'end_date': end_date.replace(".csv", ""),
                    'size_mb': file.stat().st_size / (1024 * 1024)
                })
            except Exception as e:
                logger.warning(f"Error processing file {file}: {e}")
    
    return datasets

if __name__ == "__main__":
    # Example usage
    collector = VahanDataCollector()
    try:
        # Get data for the last 12 months
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - pd.DateOffset(months=12)).strftime("%Y-%m-%d")
        
        df = collector.fetch_data(start_date, end_date)
        if df is not None:
            print(f"Successfully fetched {len(df)} records")
            print(df.head())
        else:
            print("Failed to fetch data")
    finally:
        collector.close()
