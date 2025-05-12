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
from typing import Optional, Literal
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules 
from google_places import GooglePlacesAPI
from cleaner import DataCleaner
from export import DataExporter


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
def search(
    region: str,
    keyword: str,
    mode: Literal['text', 'nearby'],
    radius: int,
    output_json: str,
    output_csv: str,
    clean: bool,
    cleaned_output: str
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


if __name__ == '__main__':
    cli() 