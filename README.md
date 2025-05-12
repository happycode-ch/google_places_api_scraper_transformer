# Google Places API Scraper

A CLI-based Python scraper using the Google Places API to collect structured data about farm shops in Canton Aargau, Switzerland. The project includes a minimal Streamlit frontend for data visualization.

## Features

- Search for farm shops using Google Places API
- Support for text search and nearby search modes
- Automatically paginate through all results using `next_page_token`
- Filter results to only include places in Canton Aargau
- Export data to JSON and CSV formats
- Clean and normalize data to a structured schema
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
├── requirements.txt     # Project dependencies
├── .env.example         # Example environment variables
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

## Notes

- The Google Places API has usage limits. Monitor your quota in the Google Cloud Console.
- The project uses an address component filter to identify places in Aargau.
- Some data fields (products, payment methods) may need additional sources. 