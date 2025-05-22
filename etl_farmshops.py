#!/usr/bin/env python3
"""
ETL script for processing Google Places API data into farmshops format.
"""

import argparse
import glob
import json
import logging
import os
import sys
from hashlib import md5
from typing import Dict, List, Any, Union, Set

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_long_name(address_components: List[Dict], level: str) -> str:
    """Extract long_name from address_components at the specified level."""
    for component in address_components:
        if level in component.get("types", []):
            return component.get("long_name", "")
    return ""

def parse_json_file(file_path: str) -> List[Dict]:
    """Parse a JSON file into a list of dictionaries."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON file: {file_path}")
        return []

def parse_csv_file(file_path: str) -> List[Dict]:
    """Parse a CSV file into a list of dictionaries."""
    try:
        import csv
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records
    except ImportError:
        logger.error("CSV module not available")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to parse CSV file {file_path}: {str(e)}")
        return []

def transform_record(record: Dict) -> Dict:
    """Transform a raw record into the target schema."""
    # Skip if record is a string
    if isinstance(record, str):
        raise ValueError(f"Record is a string value: {record}")
        
    place_id = record.get("place_id", "unknown")
    
    # Check if this is already cleaned data (has latitude/longitude fields)
    # or raw data (has geometry.location.lat/lng fields)
    if "latitude" in record and "longitude" in record:
        # Already cleaned data format
        try:
            lat = float(record.get("latitude", 0))
            lng = float(record.get("longitude", 0))
        except (ValueError, TypeError):
            logger.warning(f"Could not convert lat/lng to float for {record.get('name')}")
            lat = 0.0
            lng = 0.0
        
        address = record.get("address", "")
        
        # Check if opening_hours is already in the right format
        if isinstance(record.get("opening_hours"), dict):
            opening_hours_dict = record.get("opening_hours", {})
        else:
            # Unlikely scenario but handle anyway
            opening_hours_dict = {}
    else:
        # Raw Google Places API data format
        lat = float(record.get("geometry", {}).get("location", {}).get("lat", 0))
        lng = float(record.get("geometry", {}).get("location", {}).get("lng", 0))
        address = record.get("formatted_address", "")
        
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
    
    # Handle organic_certified field
    organic_certified = record.get("organic_certified", False)
    
    # Get payment methods if available
    payment_methods = record.get("payment_methods", [])
    
    # Create transformed record with required fields to match sample schema
    transformed = {
        "name": record.get("name", ""),
        "address": address,
        "latitude": lat,
        "longitude": lng,
        "products": products,
        "organic_certified": organic_certified,
        "payment_methods": payment_methods,
        "opening_hours": opening_hours_dict,
        "website": record.get("website", ""),
        "google_maps_url": google_maps_url
    }
    
    return transformed

def validate_schema(transformed_records: List[Dict], sample_schema_file: str) -> bool:
    """Validate transformed records against the sample schema."""
    try:
        # Load sample schema
        with open(sample_schema_file, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            
        if not sample_data:
            logger.error("Sample schema file is empty or invalid")
            return False
            
        # Get the first element as the schema reference
        schema_reference = sample_data[0] if isinstance(sample_data, list) else sample_data
        
        # Get schema keys and types
        schema_keys = set(schema_reference.keys())
        
        # Validate each transformed record
        for record in transformed_records:
            record_keys = set(record.keys())
            
            # Check if all required keys are present
            if record_keys != schema_keys:
                missing = schema_keys - record_keys
                extra = record_keys - schema_keys
                
                if missing:
                    logger.error(f"Record is missing keys: {missing}")
                if extra:
                    logger.error(f"Record has extra keys: {extra}")
                    
                logger.error(f"Validation failed for record with place_id: {record.get('place_id', 'unknown')}")
                return False
                
            # Check if types match
            for key in schema_keys:
                if not isinstance(record[key], type(schema_reference[key])):
                    logger.error(f"Type mismatch for key '{key}': expected {type(schema_reference[key])}, got {type(record[key])}")
                    logger.error(f"Validation failed for record with place_id: {record.get('place_id', 'unknown')}")
                    return False
                    
        return True
        
    except Exception as e:
        logger.error(f"Error during schema validation: {str(e)}")
        return False

def process_files(input_dir: str, sample_schema_file: str, output_file: str) -> bool:
    """Process all files in the input directory and output validated data."""
    # Find all JSON and CSV files
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    # Exclude the output file itself to avoid recursion
    json_files = [f for f in json_files if not f.endswith('farmshops_validated.json')]
    
    logger.info(f"Found {len(json_files)} JSON files and {len(csv_files)} CSV files to process")
    for json_file in json_files:
        logger.info(f"Found JSON file: {json_file}")
    for csv_file in csv_files:
        logger.info(f"Found CSV file: {csv_file}")
    
    raw_records = []
    seen_names = set()  # To avoid duplicate records
    
    # Process each JSON file
    for file_path in json_files:
        logger.info(f"Processing file: {file_path}")
        file_records = parse_json_file(file_path)
        
        if isinstance(file_records, list):
            # Filter to ensure we only have dictionary records
            dict_records = [r for r in file_records if isinstance(r, dict)]
            if len(dict_records) != len(file_records):
                logger.warning(f"Filtered out {len(file_records) - len(dict_records)} non-dictionary records from {file_path}")
            
            # Filter out duplicates based on name
            unique_records = []
            for record in dict_records:
                name = record.get('name', '')
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_records.append(record)
            
            logger.info(f"Added {len(unique_records)} unique records from {file_path}")
            raw_records.extend(unique_records)
        elif isinstance(file_records, dict):
            name = file_records.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                raw_records.append(file_records)
                logger.info(f"Added 1 record from {file_path}")
            else:
                logger.info(f"Skipped duplicate record from {file_path}")
        else:
            logger.warning(f"Skipped record with type {type(file_records)} from {file_path}")
    
    # Process each CSV file
    for file_path in csv_files:
        logger.info(f"Processing file: {file_path}")
        file_records = parse_csv_file(file_path)
        
        # Filter to ensure we only have dictionary records
        dict_records = [r for r in file_records if isinstance(r, dict)]
        if len(dict_records) != len(file_records):
            logger.warning(f"Filtered out {len(file_records) - len(dict_records)} non-dictionary records from {file_path}")
        
        # Filter out duplicates based on name
        unique_records = []
        for record in dict_records:
            name = record.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_records.append(record)
        
        logger.info(f"Added {len(unique_records)} unique records from {file_path}")
        raw_records.extend(unique_records)
    
    logger.info(f"Parsed {len(raw_records)} total unique raw records")
    
    # Make sure we have valid records to process
    if not raw_records:
        logger.error("No valid records found to process")
        return False
    
    # Transform records
    transformed_records = []
    for record in raw_records:
        try:
            transformed = transform_record(record)
            transformed_records.append(transformed)
        except Exception as e:
            logger.error(f"Error transforming record: {str(e)}")
            if 'place_id' in record:
                logger.error(f"Failed for place_id: {record['place_id']}")
    
    logger.info(f"Transformed {len(transformed_records)} records")
    
    if not transformed_records:
        logger.error("No records were successfully transformed")
        return False
    
    # Validate against schema
    if not validate_schema(transformed_records, sample_schema_file):
        logger.error("Schema validation failed")
        return False
        
    # Write output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"farmshops": transformed_records}, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully wrote {len(transformed_records)} records to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing output file: {str(e)}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="ETL script for farmshops data")
    parser.add_argument("--input-dir", required=True, help="Directory containing raw place files")
    parser.add_argument("--schema-file", required=True, help="Path to sample schema file")
    parser.add_argument("--output-file", required=True, help="Path to output file")
    
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
        
    # Check if schema file exists
    if not os.path.isfile(args.schema_file):
        logger.error(f"Schema file does not exist: {args.schema_file}")
        sys.exit(1)
        
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Process files
    success = process_files(args.input_dir, args.schema_file, args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1) 