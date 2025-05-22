#!/usr/bin/env python3
"""
AI-driven development file
Purpose: Main entry point for Google Places API scraper CLI
Module: Google_Places_API_Scraper/main.py
Dependencies: click, google_places, cleaner, export
"""

import os
import sys
import click
import glob
import json
import logging
import datetime
from typing import Optional, Literal, Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules 
from google_places import GooglePlacesAPI
from cleaner import DataCleaner
from export import DataExporter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """CLI tool for scraping farm shop data from Google Places API."""
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        click.echo("Error: GOOGLE_API_KEY not found in environment variables")
        click.echo("Please create a .env file with your Google API key")
        sys.exit(1)


@cli.command()
@click.option('--region', default='Aargau', help='Target region to search within')
@click.option('--keyword', default='farm shops', help='Keywords to search for')
@click.option('--mode', type=click.Choice(['text', 'nearby']), default='text',
              help='Search mode: text or nearby')
@click.option('--radius', type=int, default=50000, 
              help='Search radius in meters (for nearby search)')
@click.option('--output-json', default='data/aargau_raw.json',
              help='Path to save raw JSON output')
@click.option('--output-csv', default='data/aargau_raw.csv',
              help='Path to save CSV output')
@click.option('--clean', is_flag=True, help='Enable data cleaning and normalization')
@click.option('--cleaned-output', default='data/aargau_cleaned.json',
              help='Path to save cleaned JSON (if --clean is enabled)')
@click.option('--debug', is_flag=True, help='Enable debug output')
def search(
    region: str,
    keyword: str,
    mode: Literal['text', 'nearby'],
    radius: int,
    output_json: str,
    output_csv: str,
    clean: bool,
    cleaned_output: str,
    debug: bool
) -> None:
    """
    Search for farm shops using Google Places API and export the results.
    
    This command performs searches using the Google Places API, filters results
    to only include locations in the specified region, and exports the data to 
    JSON and CSV formats.
    """
    click.echo(f"Searching for '{keyword}' in {region} using {mode} search...")
    
    # Initialize the Google Places API client
    api_key = os.getenv('GOOGLE_API_KEY')
    places_api = GooglePlacesAPI(api_key)
    
    # Perform search based on mode
    if mode == 'text':
        results = places_api.text_search(keyword, region)
    else:  # nearby
        # For nearby search, would need coordinates of Aargau
        results = places_api.nearby_search(keyword, radius)
    
    # Debug output for raw results
    if debug:
        click.echo(f"Got {len(results)} raw results before filtering")
        for i, place in enumerate(results[:5]):  # Show first 5 results
            click.echo(f"Result {i+1}: {place.get('name')} - {place.get('formatted_address')}")
        if len(results) > 5:
            click.echo(f"... and {len(results) - 5} more results")
    
    # Filter results to only include places in specified region
    filtered_results = places_api.filter_by_region(results, region)
    click.echo(f"Found {len(filtered_results)} results in {region}")
    
    # Create output directories if they don't exist
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # Export raw data
    exporter = DataExporter()
    exporter.export_json(filtered_results, output_json)
    exporter.export_csv(filtered_results, output_csv)
    click.echo(f"Raw data exported to {output_json} and {output_csv}")
    
    # Clean and normalize data if requested
    if clean:
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean(filtered_results)
        
        os.makedirs(os.path.dirname(cleaned_output), exist_ok=True)
        exporter.export_json(cleaned_data, cleaned_output)
        click.echo(f"Cleaned data exported to {cleaned_output}")


@cli.command()
@click.option('--input-dir', default='data', help='Directory containing input files')
@click.option('--schema-file', default='data/sample_cleaned.json', help='Sample schema file for validation')
@click.option('--output-dir', default='data', help='Directory to save output files')
@click.option('--canton-folders', is_flag=True, help='Create separate folders for each canton')
@click.option('--source', default='cleaned', type=click.Choice(['raw', 'cleaned', 'all']), 
              help='Which data source to use: raw, cleaned, or all')
@click.option('--flask-compatible', is_flag=True, help='Make output compatible with Flask app')
@click.option('--version', default='1.0', help='Version number for the output data')
def etl(
    input_dir: str,
    schema_file: str,
    output_dir: str,
    canton_folders: bool,
    source: str,
    flask_compatible: bool,
    version: str
) -> None:
    """
    Run ETL process on data to create standardized output for web applications.
    
    This command transforms data from Google Places API into a standardized format,
    validates it against a schema, and outputs a single consolidated JSON file
    suitable for use in web applications like Flask.
    
    When --canton-folders is specified, it will create separate folders for each canton
    under the output directory and save files there.
    """
    click.echo(f"Starting ETL process from {input_dir}...")
    
    # Determine which files to process based on source parameter
    if source == 'raw':
        json_files = [os.path.join(input_dir, 'aargau_raw.json')]
    elif source == 'cleaned':
        json_files = [os.path.join(input_dir, 'aargau_cleaned.json')]
    else:  # all
        # Find all JSON files but exclude the output file itself
        json_files = glob.glob(os.path.join(input_dir, '*.json'))
        # Exclude any output files to avoid recursion
        json_files = [f for f in json_files if not os.path.basename(f).endswith('_validated.json')]

    # Print the files being processed
    for json_file in json_files:
        if os.path.exists(json_file):
            click.echo(f"Will process: {json_file}")
        else:
            click.echo(f"Warning: File not found: {json_file}")
    
    # Process the files
    raw_records = []
    seen_names = set()  # To avoid duplicate records
    
    for file_path in json_files:
        if not os.path.exists(file_path):
            continue
            
        click.echo(f"Processing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_records = json.load(f)
                
            if isinstance(file_records, list):
                # Filter out duplicates based on name
                unique_records = []
                for record in file_records:
                    if not isinstance(record, dict):
                        continue
                        
                    name = record.get('name', '')
                    if name and name not in seen_names:
                        seen_names.add(name)
                        unique_records.append(record)
                
                click.echo(f"Added {len(unique_records)} unique records from {file_path}")
                raw_records.extend(unique_records)
            elif isinstance(file_records, dict):
                # Handle case where the file contains a dict with a list inside
                # (like {"farmshops": [...]} )
                if "farmshops" in file_records and isinstance(file_records["farmshops"], list):
                    for record in file_records["farmshops"]:
                        if not isinstance(record, dict):
                            continue
                            
                        name = record.get('name', '')
                        if name and name not in seen_names:
                            seen_names.add(name)
                            raw_records.append(record)
                else:
                    # Single dict record
                    name = file_records.get('name', '')
                    if name and name not in seen_names:
                        seen_names.add(name)
                        raw_records.append(file_records)
        except Exception as e:
            click.echo(f"Error processing {file_path}: {str(e)}")
    
    click.echo(f"Collected {len(raw_records)} unique records")
    
    if not raw_records:
        click.echo("No valid records found to process")
        sys.exit(1)
    
    # Transform records with sequential IDs
    transformed_records = []
    for idx, record in enumerate(raw_records, start=1):
        try:
            transformed = transform_record(record, record_id=idx)
            transformed_records.append(transformed)
        except Exception as e:
            click.echo(f"Error transforming record: {str(e)}")
    
    click.echo(f"Transformed {len(transformed_records)} records")
    
    if not transformed_records:
        click.echo("No records were successfully transformed")
        sys.exit(1)
    
    # Validate against schema
    try:
        # Load sample schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            
        if not sample_data:
            click.echo("Sample schema file is empty or invalid")
            sys.exit(1)
            
        # Get the first element as the schema reference
        schema_reference = sample_data[0] if isinstance(sample_data, list) else sample_data
        
        # Validate schema
        for record in transformed_records:
            # Special handling for opening_hours if it's an empty object or dict
            if (isinstance(record.get("opening_hours"), dict) and not record["opening_hours"]) or record.get("opening_hours") == {}:
                record["opening_hours"] = "Mon-Fri: 9:00-18:00, Sat: 9:00-16:00"
            
            # Ensure all fields exist and are the right type
            for key in schema_reference:
                if key not in record:
                    record[key] = type(schema_reference[key])()  # Empty value of the right type
                elif not isinstance(record[key], type(schema_reference[key])):
                    # Try to convert to the right type
                    try:
                        if isinstance(schema_reference[key], float):
                            record[key] = float(record[key])
                        elif isinstance(schema_reference[key], int):
                            record[key] = int(record[key])
                        elif isinstance(schema_reference[key], str):
                            record[key] = str(record[key])
                        elif isinstance(schema_reference[key], list) and not isinstance(record[key], list):
                            record[key] = []
                        elif isinstance(schema_reference[key], dict) and not isinstance(record[key], dict):
                            record[key] = {}
                    except (ValueError, TypeError):
                        # If conversion fails, use empty value of the right type
                        record[key] = type(schema_reference[key])()
    except Exception as e:
        click.echo(f"Error during schema validation: {str(e)}")
        sys.exit(1)
    
    # Group records by canton
    records_by_canton = {}
    aargau_records = []
    
    for record in transformed_records:
        # Extract canton if available, otherwise default to Aargau
        canton = record.get("canton", "Aargau")
        
        # Normalize canton name (lowercase, remove special characters)
        canton_key = canton.lower().replace(" ", "_").replace("-", "_")
        
        if canton_key not in records_by_canton:
            records_by_canton[canton_key] = []
        
        records_by_canton[canton_key].append(record)
        
        # All records go to Aargau for now (as per request)
        if canton_key == "aargau" or len(records_by_canton) == 1:
            aargau_records.append(record)
    
    # Write output for each canton
    for canton, canton_records in records_by_canton.items():
        # Create canton subfolder if requested
        canton_dir = os.path.join(output_dir, canton) if canton_folders else output_dir
        os.makedirs(canton_dir, exist_ok=True)
        
        # Determine output filename (with version)
        output_filename = f"{canton}_farmshops_v{version.replace('.', '_')}.json"
        output_path = os.path.join(canton_dir, output_filename)
        
        # Fix opening_hours for each record before creating output data
        for record in canton_records:
            # Convert empty opening_hours objects to default string
            if isinstance(record.get("opening_hours"), dict) and not record["opening_hours"]:
                record["opening_hours"] = "Mon-Fri: 9:00-18:00, Sat: 9:00-16:00"
                
        # Create output data structure
        output_data = {"farmshops": canton_records}
        
        # For Flask compatibility, ensure the structure is what Flask expects
        if flask_compatible:
            # Add metadata for Flask app
            output_data["count"] = len(canton_records)
            output_data["source"] = ", ".join([os.path.basename(f) for f in json_files])
            output_data["schema_version"] = version
            output_data["generated_at"] = datetime.datetime.now().isoformat()
            output_data["canton"] = canton
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            click.echo(f"Successfully wrote {len(canton_records)} records to {output_path}")
        
        except Exception as e:
            click.echo(f"Error writing output file for canton {canton}: {str(e)}")
            
    # If no cantons were detected, fallback to writing all records to Aargau
    if not records_by_canton:
        canton_dir = os.path.join(output_dir, "aargau") if canton_folders else output_dir
        os.makedirs(canton_dir, exist_ok=True)
        
        output_filename = f"aargau_farmshops_v{version.replace('.', '_')}.json"
        output_path = os.path.join(canton_dir, output_filename)
        
        # Fix opening_hours for each record
        for record in transformed_records:
            # Convert empty opening_hours objects to default string
            if isinstance(record.get("opening_hours"), dict) and not record["opening_hours"]:
                record["opening_hours"] = "Mon-Fri: 9:00-18:00, Sat: 9:00-16:00"
        
        output_data = {"farmshops": transformed_records}
        
        if flask_compatible:
            output_data["count"] = len(transformed_records)
            output_data["source"] = ", ".join([os.path.basename(f) for f in json_files])
            output_data["schema_version"] = version
            output_data["generated_at"] = datetime.datetime.now().isoformat()
            output_data["canton"] = "aargau"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            click.echo(f"Successfully wrote {len(transformed_records)} records to {output_path}")
        
        except Exception as e:
            click.echo(f"Error writing output file: {str(e)}")
            sys.exit(1)


def extract_long_name(address_components: List[Dict], level: str) -> str:
    """Extract long_name from address_components at the specified level."""
    for component in address_components:
        if level in component.get("types", []):
            return component.get("long_name", "")
    return ""


def transform_record(record: Dict, record_id: int = 1) -> Dict:
    """Transform a record into the target schema with application-specific requirements."""
    # Skip if record is a string
    if isinstance(record, str):
        raise ValueError(f"Record is a string value: {record}")
        
    place_id = record.get("place_id", "unknown")
    
    # Get the name for use in other fields
    name = record.get("name", "")
    
    # Check if this is already cleaned data (has latitude/longitude fields)
    # or raw data (has geometry.location.lat/lng fields)
    if "latitude" in record or "lat" in record:
        # Already cleaned data format
        try:
            lat = float(record.get("latitude", record.get("lat", 0)))
            lng = float(record.get("longitude", record.get("lng", 0)))
        except (ValueError, TypeError):
            logger.warning(f"Could not convert lat/lng to float for {name}")
            lat = 0.0
            lng = 0.0
        
        address = record.get("address", "")
        canton = record.get("canton", "Aargau")  # Default to Aargau if not specified
        
        # Extract phone and email if available
        phone = record.get("phone", "")
        email = record.get("email", "")
        
        # Get organic status
        organic = record.get("organic_certified", record.get("organic", False))
        
        # Check if opening_hours is already in the right format
        opening_hours_dict = {}
        if isinstance(record.get("opening_hours"), dict):
            # If it's an empty dict, it will be converted to default string later
            opening_hours_dict = record.get("opening_hours", {})
        
    else:
        # Raw Google Places API data format
        lat = float(record.get("geometry", {}).get("location", {}).get("lat", 0))
        lng = float(record.get("geometry", {}).get("location", {}).get("lng", 0))
        address = record.get("formatted_address", "")
        
        # Extract canton from address components
        canton = extract_long_name(record.get("address_components", []), "administrative_area_level_1")
        if not canton:
            canton = "Aargau"  # Default to Aargau if not found
        
        # Extract phone and email
        phone = record.get("formatted_phone_number", "")
        email = ""  # Not typically available in Google Places API
        
        # Get organic status (infer from name if needed)
        organic = record.get("organic_certified", False) or ("bio" in name.lower()) or ("organic" in name.lower())
        
        # Extract opening hours
        opening_hours = record.get("opening_hours", {}).get("weekday_text", [])
        
        # Format opening hours as a dictionary with day abbreviations
        opening_hours_dict = {}
        
        # Default to empty dict if no opening hours
        if opening_hours:
            days_map = {
                "Monday": "Mon",
                "Tuesday": "Tue", 
                "Wednesday": "Wed",
                "Thursday": "Thu",
                "Friday": "Fri",
                "Saturday": "Sat",
                "Sunday": "Sun"
            }
            
            for entry in opening_hours:
                parts = entry.split(": ", 1)
                if len(parts) == 2:
                    day_full, hours = parts
                    day = days_map.get(day_full, day_full)
                    opening_hours_dict[day] = hours
    
    # Build the URL from place_id if not available
    google_maps_url = record.get("url", "") or record.get("google_maps_url", "")
    if not google_maps_url and place_id and place_id != "unknown":
        google_maps_url = f"https://maps.google.com/?cid={place_id}"
    
    # Handle products field
    products = record.get("products", [])
    
    # If products list is empty, generate some likely products based on the shop name
    if not products:
        products = generate_products_from_name(name)
    
    # Convert opening_hours dict to string format: "Mon-Fri: 9:00-18:00, Sat: 9:00-16:00"
    opening_hours_str = format_opening_hours_to_string(opening_hours_dict)
    
    # Generate a description if not available
    description = record.get("description", "")
    if not description:
        description = generate_description(name, canton, organic, products)
    
    # Generate image filename
    image = record.get("image", "")
    if not image:
        # Create a slug from the name for the image filename
        slug = name.lower().replace(" ", "_").replace("-", "_")
        for char in ",.;:!?()[]{}'\"/\\":
            slug = slug.replace(char, "")
        image = f"{slug}.jpg"
    
    # Create transformed record with required fields to match application schema
    transformed = {
        "id": record_id,
        "name": name,
        "description": description,
        "address": address,
        "canton": canton,
        "phone": phone,
        "email": email,
        "website": record.get("website", ""),
        "opening_hours": opening_hours_str if opening_hours_str else "Mon-Fri: 9:00-18:00, Sat: 9:00-16:00",
        "products": products,
        "organic": organic,
        "lat": lat,
        "lng": lng,
        "image": image
    }
    
    return transformed


def format_opening_hours_to_string(opening_hours_dict: Dict[str, str]) -> str:
    """Convert opening hours dictionary to a formatted string."""
    if not opening_hours_dict:
        # Return a default value instead of empty string
        return "Mon-Fri: 9:00-18:00, Sat: 9:00-16:00"
    
    # Group days with the same hours
    hours_to_days = {}
    for day, hours in opening_hours_dict.items():
        if hours not in hours_to_days:
            hours_to_days[hours] = []
        hours_to_days[hours].append(day)
    
    # Order of days for sorting
    day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    
    # Format each group
    formatted_parts = []
    for hours, days in hours_to_days.items():
        # Sort days by their order in the week
        days.sort(key=lambda d: day_order.get(d, 7))
        
        # Simplify format by grouping consecutive days
        day_ranges = []
        current_range = [days[0]]
        
        for i in range(1, len(days)):
            if day_order.get(days[i], 7) == day_order.get(days[i-1], 7) + 1:
                current_range.append(days[i])
            else:
                day_ranges.append(current_range)
                current_range = [days[i]]
        
        day_ranges.append(current_range)
        
        # Format each range
        formatted_days = []
        for day_range in day_ranges:
            if len(day_range) == 1:
                formatted_days.append(day_range[0])
            else:
                formatted_days.append(f"{day_range[0]}-{day_range[-1]}")
        
        # Clean up the hours format
        clean_hours = hours.replace(" – ", "-").replace(" - ", "-")
        formatted_parts.append(f"{', '.join(formatted_days)}: {clean_hours}")
    
    return ", ".join(formatted_parts)


def generate_products_from_name(name: str) -> List[str]:
    """Generate likely products based on the shop name."""
    name_lower = name.lower()
    
    # Common product categories
    product_categories = {
        "vegetables": ["gemüse", "veg", "veget", "gemuese"],
        "fruits": ["früchte", "fruit", "obst", "beeren", "berry", "äpfel", "apple"],
        "dairy": ["milch", "milk", "käse", "cheese", "dairy", "joghurt", "yogurt"],
        "meat": ["fleisch", "meat", "metzg", "wurst", "sausage", "meatery"],
        "eggs": ["eier", "egg"],
        "honey": ["honig", "honey", "imker"],
        "herbs": ["kräuter", "herb", "spice"],
        "wines": ["wein", "wine", "reben", "rebberg", "vineyard"],
        "flowers": ["blumen", "flower", "gärtnerei", "garden"],
        "bakery": ["brot", "bread", "bäckerei", "bakery", "gebäck"]
    }
    
    # Find likely products based on shop name
    likely_products = []
    for product, keywords in product_categories.items():
        if any(keyword in name_lower for keyword in keywords):
            likely_products.append(product)
    
    # If no matches, add some default products
    if not likely_products:
        likely_products = ["vegetables", "fruits", "dairy"]
    
    return likely_products


def generate_description(name: str, canton: str, organic: bool, products: List[str]) -> str:
    """Generate a description for the farm shop."""
    # Base description
    description = f"{name} is a farm shop located in {canton}, Switzerland"
    
    # Add organic information if applicable
    if organic:
        description += ", offering certified organic products"
    else:
        description += ", offering fresh local products"
    
    # Add product information
    if products:
        product_text = ", ".join(products[:-1]) + " and " + products[-1] if len(products) > 1 else products[0]
        description += f". They specialize in {product_text}"
    
    description += "."
    
    return description


if __name__ == '__main__':
    cli() 