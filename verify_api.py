#!/usr/bin/env python3
"""
AI-driven development file
Purpose: Verify Google Places API key and configuration
Module: Google_Places_API_Scraper/verify_api.py
Dependencies: requests, dotenv
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Tuple

# Load environment variables
load_dotenv()

# Google API endpoints
PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def check_api_key() -> Tuple[bool, str]:
    """
    Check if the API key is present in the environment.
    
    Returns:
        Tuple of (success, message)
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        return False, "API key not found in environment variables. Check your .env file."
    
    if api_key == "your-api-key-here":
        return False, "API key is still the default placeholder. Please update with a real key."
    
    # Mask API key for display
    masked_key = api_key[:4] + '****' + api_key[-4:] if len(api_key) > 8 else '****'
    return True, f"API key found: {masked_key}"


def test_simple_request() -> Tuple[bool, Dict[str, Any], str]:
    """
    Make a very simple Places API request to verify the key and billing.
    
    Returns:
        Tuple of (success, response_data, message)
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    
    # Use minimal parameters to test the key
    params = {
        "query": "restaurant",
        "key": api_key
    }
    
    try:
        response = requests.get(PLACES_TEXT_SEARCH_URL, params=params)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get("error_message", "Unknown error")
            status = data.get("status", "UNKNOWN_ERROR")
            return False, data, f"API error: {status} - {error_msg}"
            
        # If we get here, the request was successful
        return True, data, "API request successful"
        
    except Exception as e:
        return False, {}, f"Exception making API request: {str(e)}"


def test_farm_shop_request() -> Tuple[bool, Dict[str, Any], str]:
    """
    Make a request with the exact parameters used in the main program.
    
    Returns:
        Tuple of (success, response_data, message)
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    
    search_query = "farm shop in Aargau Switzerland"
    params = {
        "query": search_query,
        "key": api_key
    }
    
    try:
        print(f"Testing with query: '{search_query}'")
        response = requests.get(PLACES_TEXT_SEARCH_URL, params=params)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get("error_message", "Unknown error")
            status = data.get("status", "UNKNOWN_ERROR")
            return False, data, f"API error: {status} - {error_msg}"
        
        # Check status field in response
        status = data.get("status", "")
        if status != "OK" and status != "ZERO_RESULTS":
            error_msg = data.get("error_message", "Unknown error")
            return False, data, f"API error: {status} - {error_msg}"
            
        # If we get here, the request was successful
        num_results = len(data.get("results", []))
        return True, data, f"API request successful, found {num_results} results"
        
    except Exception as e:
        return False, {}, f"Exception making API request: {str(e)}"


def check_api_status() -> Dict[str, Any]:
    """
    Run a series of checks for the Google Places API configuration.
    
    Returns:
        Dictionary with check results
    """
    results = {
        "api_key_present": False,
        "api_key_message": "",
        "api_request_success": False,
        "api_request_message": "",
        "farm_shop_request_success": False,
        "farm_shop_request_message": "",
        "api_response": {},
        "farm_shop_response": {},
        "billing_enabled": False,
        "places_api_enabled": False,
        "overall_status": "FAILED",
        "recommendations": []
    }
    
    # Check if API key is present
    results["api_key_present"], results["api_key_message"] = check_api_key()
    
    if not results["api_key_present"]:
        results["recommendations"].append("Add a valid Google API key to your .env file")
        return results
    
    # Test a simple API request
    results["api_request_success"], results["api_response"], results["api_request_message"] = test_simple_request()
    
    # Test the farm shop request
    results["farm_shop_request_success"], results["farm_shop_response"], results["farm_shop_request_message"] = test_farm_shop_request()
    
    # Analyze the response to determine status based on both tests
    has_error = not results["api_request_success"] or not results["farm_shop_request_success"]
    
    if has_error:
        # Check both responses for errors
        for response_type in ["api_response", "farm_shop_response"]:
            api_status = results[response_type].get("status", "")
            error_message = results[response_type].get("error_message", "")
            
            if error_message:  # Only process if there was an error
                if "API key is invalid" in error_message or api_status == "REQUEST_DENIED":
                    if "The API key is invalid or restricted. Generate a new API key." not in results["recommendations"]:
                        results["recommendations"].append("The API key is invalid or restricted. Generate a new API key.")
                
                if "billing" in error_message.lower():
                    if "Enable billing for your Google Cloud project." not in results["recommendations"]:
                        results["recommendations"].append("Enable billing for your Google Cloud project.")
                
                if "This API project is not authorized to use this API" in error_message:
                    if "Enable the Places API for this project in the Google Cloud Console." not in results["recommendations"]:
                        results["recommendations"].append("Enable the Places API for this project in the Google Cloud Console.")
        
        if not results["recommendations"]:
            results["recommendations"].append("Check the Google Cloud Console for more details on the error.")
    else:
        results["billing_enabled"] = True
        results["places_api_enabled"] = True
        results["overall_status"] = "SUCCESS"
        results["recommendations"].append("Your API key is working correctly. You can now use the scraper.")
    
    return results


def main():
    """Main function to run the verification."""
    print("Google Places API Verification")
    print("=============================")
    
    status = check_api_status()
    
    print(f"\nAPI Key Check: {'✓' if status['api_key_present'] else '✗'}")
    print(f"  {status['api_key_message']}")
    
    print(f"\nBasic API Request: {'✓' if status['api_request_success'] else '✗'}")
    print(f"  {status['api_request_message']}")
    
    print(f"\nFarm Shop API Request: {'✓' if status['farm_shop_request_success'] else '✗'}")
    print(f"  {status['farm_shop_request_message']}")
    
    print(f"\nBilling Enabled: {'✓' if status['billing_enabled'] else '?'}")
    print(f"Places API Enabled: {'✓' if status['places_api_enabled'] else '?'}")
    
    print(f"\nOverall Status: {status['overall_status']}")
    
    if status["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(status["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    # Print full responses for debugging if there was an error
    if not status["api_request_success"] and status["api_response"]:
        print("\nBasic API Response:")
        print(json.dumps(status["api_response"], indent=2))
    
    if not status["farm_shop_request_success"] and status["farm_shop_response"]:
        print("\nFarm Shop API Response:")
        print(json.dumps(status["farm_shop_response"], indent=2))


if __name__ == "__main__":
    main() 