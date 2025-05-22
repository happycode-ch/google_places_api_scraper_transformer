#!/usr/bin/env python3
"""
AI-driven development file
Purpose: Check which Google APIs are accessible with the current API key
Module: Google_Places_API_Scraper/check_api_details.py
Dependencies: requests, dotenv
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test multiple Google APIs to see which ones are accessible
APIS_TO_TEST = [
    {
        "name": "Places API (Text Search)",
        "url": "https://maps.googleapis.com/maps/api/place/textsearch/json",
        "params": {"query": "restaurant", "key": ""}
    },
    {
        "name": "Places API (Nearby Search)",
        "url": "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        "params": {"location": "47.3887,8.0558", "radius": "1000", "key": ""}
    },
    {
        "name": "Places API (Details)",
        "url": "https://maps.googleapis.com/maps/api/place/details/json",
        "params": {"place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4", "fields": "name", "key": ""}
    },
    {
        "name": "Geocoding API",
        "url": "https://maps.googleapis.com/maps/api/geocode/json",
        "params": {"address": "Zurich, Switzerland", "key": ""}
    },
    {
        "name": "Directions API",
        "url": "https://maps.googleapis.com/maps/api/directions/json",
        "params": {"origin": "Zurich", "destination": "Bern", "key": ""}
    },
    {
        "name": "Maps JavaScript API",
        "url": "https://maps.googleapis.com/maps/api/js",
        "params": {"key": ""}
    }
]

def main():
    """Test which Google APIs are accessible with the current API key."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("No API key found in .env file")
        return
    
    # Mask API key for display
    masked_key = api_key[:4] + '****' + api_key[-4:] if len(api_key) > 8 else '****'
    print(f"Testing API key: {masked_key}\n")
    
    # Test each API
    print("API ACCESS TEST RESULTS:")
    print("=" * 50)
    for api in APIS_TO_TEST:
        print(f"\nTesting {api['name']}...")
        
        # Add the API key to the parameters
        params = api['params'].copy()
        params['key'] = api_key
        
        # Make request
        try:
            response = requests.get(api['url'], params=params)
            data = response.json() if 'json' in response.headers.get('content-type', '') else {'status': 'Unknown'}
            
            status = data.get('status', 'UNKNOWN')
            if response.status_code == 200 and (status == 'OK' or status == 'ZERO_RESULTS' or 'error_message' not in data):
                print(f"✓ SUCCESS: Status code {response.status_code}, API status: {status}")
            else:
                error = data.get('error_message', data.get('error', 'Unknown error'))
                print(f"✗ FAILED: Status code {response.status_code}, Error: {error}")
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")

if __name__ == "__main__":
    main() 