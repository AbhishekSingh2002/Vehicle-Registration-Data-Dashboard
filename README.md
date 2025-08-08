# 🚗 Vehicle Registration Data Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-url.streamlit.app/)

A comprehensive dashboard for analyzing vehicle registration data from the Vahan Dashboard, featuring YoY/QoQ growth metrics, manufacturer insights, and interactive visualizations.

## 📋 Features

- **Interactive Filters**
  - Date range selection
  - Vehicle type (2W/3W/4W)
  - Manufacturer selection
  - State/Region filtering

- **Key Metrics**
  - Total registrations by category
  - Year-over-Year (YoY) growth
  - Quarter-over-Quarter (QoQ) growth
  - Market share analysis

- **Visualizations**
  - Time series trends
  - Category-wise distribution
  - Manufacturer performance
  - Growth metrics

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Vehicle-Registration-Data-Dashboard.git
   cd Vehicle-Registration-Data-Dashboard
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory with:
   ```
   # Vahan API Credentials
   VAHAN_API_KEY=your_api_key_here
   
   # Optional: Database configuration
   DB_URI=sqlite:///data/vehicle_data.db
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📊 Data Assumptions

1. **Data Source**
   - Data is sourced from the Vahan Dashboard public API
   - Sample data is used when API is not accessible

2. **Data Processing**
   - Dates are normalized to the first day of each month
   - Missing values are filled with zeros
   - All monetary values are in INR (Indian Rupees)

3. **Limitations**
   - Real-time data depends on Vahan API availability
   - Historical data might be limited by API constraints

## 🛣️ Feature Roadmap

### Phase 1: Core Functionality ✅
- [x] Basic dashboard layout
- [x] Data filtering and visualization
- [x] YoY/QoQ growth calculations

### Phase 2: Enhanced Analytics (In Progress) 🔄
- [ ] Advanced time series forecasting
- [ ] Regional analysis
- [ ] Export functionality

### Phase 3: Enterprise Features (Planned) 📅
- [ ] User authentication
- [ ] Scheduled data updates
- [ ] Custom report generation

## 📝 Testing

### Unit Tests
```bash
pytest tests/
```

### Test Coverage
```bash
pytest --cov=src tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Vahan Dashboard for providing the data
- Streamlit for the amazing dashboard framework
- All contributors who helped improve this project

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
