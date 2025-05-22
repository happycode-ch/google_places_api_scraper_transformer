# Farmshops ETL Script

This script processes Google Places API data into a standardized farmshops format.

## Usage

```bash
python etl_farmshops.py --input-dir <path_to_raw_places_files> --schema-file <path_to>/farmshops_sample.json --output-file <path_to>/farmshops_validated.json
```

## Arguments

- `--input-dir`: Directory containing raw JSON/CSV files from Google Places API
- `--schema-file`: Path to the sample schema file (e.g., farmshops_sample.json)
- `--output-file`: Path where the validated output will be written

## Process

1. **Ingest & Parse**: The script finds all JSON and CSV files in the input directory and parses them.

2. **Map & Transform**: Each raw record is transformed to match the required schema:
   - `id`: Computed as abs(hash(place_id))
   - `name`: From original data
   - `description`: Empty string
   - `address`: From "formatted_address"
   - `canton`: Extracted from address_components at level "administrative_area_level_1"
   - `phone`: From "formatted_phone_number" or empty string
   - `email`: Empty string
   - `website`: From original data or empty string
   - `opening_hours`: Joined weekday_text with commas
   - `products`: Empty array
   - `organic`: False
   - `lat`: Float from geometry.location.lat
   - `lng`: Float from geometry.location.lng
   - `image`: Empty string

3. **Validate Against Sample**: Ensures all transformed records match the schema.

4. **Write Output**: Writes the validated data to the specified output file.

## Dependencies

Only standard library modules are used. 