# Vehicle Registration Data Dashboard

A Streamlit-based dashboard for analyzing vehicle registration data from the Vahan Dashboard.

## Features

- Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth analysis
- Vehicle type-wise registration data (2W, 3W, 4W)
- Manufacturer-wise registration data
- Interactive date range selection
- Data visualization with charts and tables

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Data Collection

Data is collected from the Vahan Dashboard (https://vahan.parivahan.gov.in/vahan4dashboard/).

## Project Structure

```
.
├── data/                   # Raw and processed data
├── src/
│   ├── __init__.py
│   ├── data_collection.py  # Data scraping/extraction logic
│   ├── data_processing.py  # Data cleaning and processing
│   └── utils.py            # Utility functions
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md
```
