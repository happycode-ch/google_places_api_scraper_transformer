Understood. Below is a single, copy-pasteable standalone Markdown document that serves as your Cursor AI Agent Prompt for building a CLI-first Google Places API scraper, with a minimal Streamlit frontend as a second-phase feature.

⸻


# 🤖 GOOGLE_PLACES_API_SCRAPER.md

## 🧭 Objective

You are an autonomous agent working in Cursor AI. Your task is to fully set up and build a CLI-based Python scraper using the **Google Places API** to collect structured data about **farm shops** in **Canton Aargau, Switzerland**. After the CLI is functional and tested, you will build a **minimal Streamlit frontend** that allows review and basic interaction with the scraped data.

This scraper will support my larger `farmshops.ch` directory project but is designed as a **standalone utility**, housed in:

Project Name: Google Places API Scraper
Project Root: ~/Code/Google_Places_API_Scraper/

The entire stack must remain lean, modular, and human-readable.

---

## 🔐 Google Cloud Setup — CLI Only

You must perform **all setup using the `gcloud` CLI**, not the Google web console. Automate everything.

1. ✅ Check if `gcloud` CLI is installed; install if missing.
2. ✅ Create/select project:
   ```bash
   gcloud projects create farmshops-cli --set-as-default

	3.	✅ Enable Places API:

gcloud services enable places-backend.googleapis.com


	4.	✅ Create an API key:

gcloud alpha services api-keys create \
  --display-name="Places API Key for FarmShops" \
  --restrictions=apiTarget=places-backend.googleapis.com


	5.	✅ Save the key in a .env file:

GOOGLE_API_KEY=your-key-here



⸻

🧩 Functionality

The scraper must:
	•	Use either:
	•	Text Search: e.g., "farm shops in Aargau Switzerland"
	•	Nearby Search: if a lat/lng grid is needed
	•	Page through all results using next_page_token
	•	Use Place Details API to filter only results in Canton Aargau
	•	Extract structured fields into:
	•	aargau_raw.json
	•	aargau_raw.csv (flattened for Excel)
	•	Optional: aargau_cleaned.json

Fields to extract:

Field	Description
name	Place name
formatted_address	Full address
latitude, longitude	Coordinates
place_id	Google Place identifier
types	Business type (for filtering)
website	Business site (if available)
url	Google Maps link
opening_hours	Human-readable hours
address_components	Used to confirm location is in Aargau

Final output schema (cleaned):

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


⸻

🖥️ CLI Requirements

Use argparse or click to build a CLI that supports:

python main.py search \
  --region "Aargau" \
  --keyword "farm shops" \
  --mode text \
  --output-json data/aargau_raw.json \
  --output-csv data/aargau_raw.csv

CLI Flags:
	•	--region: Target region, default "Aargau"
	•	--keyword: Default "farm shops"
	•	--mode: "text" or "nearby"
	•	--radius: Optional, for nearby search (in meters)
	•	--output-json: Path to save raw JSON
	•	--output-csv: Path to save a flat CSV for Excel
	•	--clean: Flag to enable schema normalization and output *_cleaned.json

⸻

🧱 File Structure

Use the following layout:

Google_Places_API_Scraper/
├── main.py              # CLI entry
├── google_places.py     # Search + Place Details
├── cleaner.py           # Normalize to schema
├── geo_utils.py         # Aargau filtering, if needed
├── export.py            # JSON and CSV writers
├── data/                # Output files
│   ├── aargau_raw.json
│   ├── aargau_raw.csv
│   └── aargau_cleaned.json
├── streamlit_app.py     # Basic Streamlit frontend (see below)
└── .env                 # Contains GOOGLE_API_KEY


⸻

🌐 Streamlit Frontend (Phase 2)

Once the CLI is tested and working, create a minimal streamlit_app.py with the following functionality:
	•	Load either aargau_raw.json or aargau_cleaned.json
	•	Display entries in a table with columns: name, address, lat/lng, website
	•	Add checkbox to filter only entries with websites
	•	Optional: show map with pins (Streamlit + pydeck or folium)

Example command:

streamlit run streamlit_app.py

No admin panel or write-back required — just view and filter.

⸻

🔒 Environment & Dependencies
	•	Python 3.11+
	•	requests, dotenv, click, pandas, streamlit (install only as needed)
	•	Keep requirements.txt minimal and CLI-first

⸻

✅ Completion Criteria

The agent has succeeded when:
	1.	The full CLI scraper runs from main.py and outputs JSON + CSV
	2.	Data is deduplicated and filtered to Aargau
	3.	Output conforms to schema and can be used in farmshops.ch
	4.	Streamlit app launches and shows the results cleanly

⸻

🧠 Development Philosophy
	•	Zero bloat
	•	CLI-first, Streamlit second
	•	Decoupled output → usable by farmshops.ch or any other project
	•	Everything automatable, nothing locked to a GUI
	•	Built for a human developer to review, not just a bot to run

⸻

💡 Cursor Agent: Think like an engineer, act like a builder. If you’re unsure about a query limit, deduplication method, or CLI convention, make an intelligent default and document it clearly.

