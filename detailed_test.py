#!/usr/bin/env python3
"""
AI-driven development file
Purpose: Detailed Google Places API test with verbose debugging
Module: Google_Places_API_Scraper/detailed_test.py
Dependencies: requests, json, dotenv
"""

import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Tuple

# Load environment variables
load_dotenv()

# Set constants
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def get_api_info(api_key: str) -> Dict[str, Any]:
    """Get detailed information about the API key."""
    # Mask API key for secure display
    masked_key = api_key[:4] + '****' + api_key[-4:] if len(api_key) > 8 else '****'
    
    # Print key info
    print("\n==== API KEY INFORMATION ====")
    print(f"API Key: {masked_key}")
    print(f"Key Length: {len(api_key)} characters")
    
    # Check if key follows expected format (rough check)
    looks_valid = api_key.startswith("AIza") and len(api_key) >= 30
    print(f"Key Format Check: {'✓ Looks valid' if looks_valid else '✗ Invalid format'}")
    
    return {
        "masked_key": masked_key,
        "length": len(api_key),
        "looks_valid": looks_valid
    }


def make_test_request(
    api_key: str, 
    query: str = "restaurants", 
    location: Optional[Tuple[float, float]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Make a detailed test request to the Places API.
    
    Args:
        api_key: The Google API key to test
        query: The search query to use
        location: Optional tuple of (lat, lng) to center search
        verbose: Whether to print verbose output
    
    Returns:
        Dictionary with test results
    """
    # Base params
    params = {
        "query": query,
        "key": api_key
    }
    
    # Add location if provided
    if location:
        params["location"] = f"{location[0]},{location[1]}"
        
    # Log request details if verbose
    if verbose:
        print("\n==== REQUEST DETAILS ====")
        print(f"URL: {PLACES_API_URL}")
        # Don't print the actual API key
        safe_params = params.copy()
        safe_params["key"] = "[MASKED]"
        print(f"Parameters: {json.dumps(safe_params, indent=2)}")
    
    # Make the request
    try:
        if verbose:
            print("\n==== MAKING API REQUEST ====")
        
        response = requests.get(PLACES_API_URL, params=params)
        data = response.json()
        
        # Extract status
        status_code = response.status_code
        api_status = data.get("status", "UNKNOWN")
        error_message = data.get("error_message", "None")
        
        # Log response details if verbose
        if verbose:
            print("\n==== RESPONSE DETAILS ====")
            print(f"HTTP Status: {status_code}")
            print(f"API Status: {api_status}")
            print(f"Error Message: {error_message}")
            
            # Print headers for debugging
            print("\n==== RESPONSE HEADERS ====")
            for key, value in response.headers.items():
                print(f"{key}: {value}")
                
        # Check for specific errors
        if api_status == "REQUEST_DENIED":
            if "API project is not authorized to use this API" in error_message:
                if verbose:
                    print("\n⚠️ ERROR DIAGNOSIS: Places API is not enabled for this project")
                    print("Solution: Go to Google Cloud Console > APIs & Services > Library > Enable 'Places API'")
            elif "API key not valid" in error_message:
                if verbose:
                    print("\n⚠️ ERROR DIAGNOSIS: Invalid API key")
                    print("Solution: Generate a new API key in Google Cloud Console")
            elif "billing" in error_message.lower():
                if verbose:
                    print("\n⚠️ ERROR DIAGNOSIS: Billing not enabled")
                    print("Solution: Enable billing for your Google Cloud project")
        
        # Analyze results if successful
        if api_status == "OK":
            results = data.get("results", [])
            if verbose:
                print(f"\nFound {len(results)} results")
                if results:
                    print("\nFirst result preview:")
                    first_result = results[0]
                    print(f"Name: {first_result.get('name', 'N/A')}")
                    print(f"Address: {first_result.get('formatted_address', 'N/A')}")
        
        return {
            "status_code": status_code,
            "api_status": api_status,
            "error_message": error_message,
            "success": api_status == "OK",
            "data": data
        }
        
    except Exception as e:
        if verbose:
            print(f"\n❌ EXCEPTION: {str(e)}")
        return {
            "status_code": -1,
            "api_status": "ERROR",
            "error_message": str(e),
            "success": False,
            "data": {}
        }


def main():
    """Run the detailed API test."""
    print("==== GOOGLE PLACES API DETAILED TEST ====")
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: No API key found in .env file")
        return
    
    # Get API key info
    api_info = get_api_info(api_key)
    
    # Run generic test
    print("\n===== GENERIC API TEST =====")
    generic_test = make_test_request(api_key, "restaurants")
    
    # Run farm shop specific test
    print("\n===== FARM SHOP TEST =====")
    farm_shop_test = make_test_request(api_key, "farm shop in Aargau Switzerland")
    
    # Run Aargau location-based test
    print("\n===== LOCATION-BASED TEST =====")
    location_test = make_test_request(
        api_key, 
        "farm shop", 
        location=(47.3887, 8.0558)  # Aargau coordinates
    )
    
    # Final summary
    print("\n===== TEST SUMMARY =====")
    print(f"Generic Test: {'✓ SUCCESS' if generic_test['success'] else '✗ FAILED'}")
    print(f"Farm Shop Test: {'✓ SUCCESS' if farm_shop_test['success'] else '✗ FAILED'}")
    print(f"Location Test: {'✓ SUCCESS' if location_test['success'] else '✗ FAILED'}")
    
    # Display diagnosis
    print("\n===== DIAGNOSIS =====")
    if not generic_test['success'] and not farm_shop_test['success'] and not location_test['success']:
        print("❌ All tests failed. The Places API is likely not enabled for this project.")
        print("   Go to Google Cloud Console > APIs & Services > Library > Enable 'Places API'")
    elif generic_test['success'] and not farm_shop_test['success']:
        print("⚠️ Generic test passed but specific tests failed. Check your search parameters.")
    elif generic_test['success'] and farm_shop_test['success']:
        print("✅ API is working correctly. You can now use the Google Places API scraper.")


if __name__ == "__main__":
    main() 