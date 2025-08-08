import pytest
from datetime import datetime, timedelta
import pandas as pd
from src.data_collection import VahanDataCollector

def test_data_collector_initialization():
    """Test that the data collector initializes correctly."""
    collector = VahanDataCollector(use_selenium=False)
    assert collector is not None
    assert collector.use_selenium is False
    assert collector.driver is None
    assert collector.session is not None

def test_generate_sample_data():
    """Test sample data generation."""
    collector = VahanDataCollector(use_selenium=False)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = collector._generate_sample_data(start_date, end_date)
    
    assert not df.empty
    assert 'date' in df.columns
    assert 'vehicle_type' in df.columns
    assert 'manufacturer' in df.columns
    assert 'registrations' in df.columns
    assert len(df['date'].dt.date.unique()) > 0

def test_fetch_vehicle_registrations():
    """Test fetching vehicle registrations with sample data fallback."""
    collector = VahanDataCollector(use_selenium=False)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Test with sample data fallback
    df = collector.fetch_vehicle_registrations(
        state="MH",
        vehicle_type="2W",
        fuel_type="Petrol",
        start_date=start_date,
        end_date=end_date
    )
    
    assert not df.empty
    assert 'date' in df.columns
    assert 'vehicle_type' in df.columns
    assert 'registrations' in df.columns
    assert isinstance(df, pd.DataFrame)

def test_caching():
    """Test caching functionality."""
    collector = VahanDataCollector(use_selenium=False)
    test_data = {"test": [1, 2, 3]}
    cache_key = "test_cache"
    
    # Test saving to cache
    collector._save_to_cache(cache_key, test_data)
    
    # Test reading from cache
    cached_data = collector._get_cached_data(cache_key)
    assert cached_data == test_data
    
    # Test cache expiration
    cached_data = collector._get_cached_data(cache_key, max_age_hours=0)
    assert cached_data is None

# Run with: python -m pytest tests/test_data_collection.py -v
