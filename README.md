# Google Places API Scraper

A CLI-based Python scraper using the Google Places API to collect structured data about farm shops in Canton Aargau, Switzerland. The project includes a minimal Streamlit frontend for data visualization and ETL capabilities for data transformation.

## Features

- Search for farm shops using Google Places API
- Support for text search and nearby search modes
- Automatically paginate through all results using `next_page_token`
- Filter results to only include places in Canton Aargau
- Export data to JSON and CSV formats
- Clean and normalize data to a structured schema
- ETL pipeline for transforming data into standardized formats
- API verification tools to check access and permissions
- Visualize data through a Streamlit frontend with filtering options
- Display shops on an interactive map

## Project Structure

```
Google_Places_API_Scraper/
├── main.py              # CLI entry point
├── google_places.py     # Google Places API interaction
├── cleaner.py           # Data normalization
├── geo_utils.py         # Geographic utilities
├── export.py            # JSON and CSV export
├── streamlit_app.py     # Streamlit frontend
├── check_api_details.py # API verification tool
├── etl_farmshops.py     # ETL pipeline
├── requirements.txt     # Project dependencies
├── .env.example         # Example environment variables
├── README_etl.md        # ETL documentation
├── data/                # Output directory
    ├── aargau_raw.json  # Raw data output
    ├── aargau_raw.csv   # CSV export
    └── aargau_cleaned.json # Cleaned data
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Linux/macOS
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google Cloud API key:
   - Create a project in Google Cloud Console
   - Enable the Places API
   - Create an API key with Places API restriction
   - Copy `.env.example` to `.env` and add your API key:
     ```bash
     cp .env.example .env
     # Edit .env with your API key
     ```

4. Verify the environment setup:
   ```bash
   python test_env.py
   ```

## Usage

### CLI

```bash
# Basic text search
python main.py search --region "Aargau" --keyword "farm shops"

# Nearby search with custom radius
python main.py search --mode nearby --radius 30000

# Clean and normalize data
python main.py search --clean

# Custom output paths
python main.py search --output-json "custom/path/results.json" --output-csv "custom/path/results.csv"

# Run ETL process
python main.py etl --input-dir data --output-dir processed --canton-folders --flask-compatible

# Verify API access
python check_api_details.py
```

### Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

The Streamlit app provides:
- Table view of the farm shops
- Option to filter shops with websites
- Interactive map showing shop locations

## Data Schema

Raw data includes:
- name
- formatted_address
- latitude/longitude
- place_id
- types
- website
- google_maps_url
- opening_hours
- address_components

Cleaned data follows this schema:
```json
{
  "name": "...",
  "address": "...",
  "latitude": 47.38,
  "longitude": 8.05,
  "products": [],
  "organic_certified": false,
  "payment_methods": [],
  "opening_hours": {
    "Mon": "08:00–18:00",
    "Tue": "08:00–18:00"
  },
  "website": "https://example.com",
  "google_maps_url": "https://maps.google.com/?q=Hofladen+..."
}
```

## ETL Pipeline

The ETL pipeline (`main.py etl`) provides:
- Data transformation from Google Places API format to standardized schema
- Support for multiple cantons with separate output folders
- Flask-compatible output format with metadata
- Schema validation and data cleaning
- Automatic handling of missing or invalid data
- Version control for output files

See `README_etl.md` for detailed ETL documentation.

## API Verification

The `check_api_details.py` script helps verify:
- API key validity
- Access to different Google APIs
- Specific permissions and quotas
- API response status and errors

## Notes

- The Google Places API has usage limits. Monitor your quota in the Google Cloud Console.
- The project uses an address component filter to identify places in Aargau.
- Some data fields (products, payment methods) may need additional sources. 