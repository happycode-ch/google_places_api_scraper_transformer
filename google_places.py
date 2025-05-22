"""
AI-driven development file
Purpose: Google Places API interaction module for farm shop data retrieval
Module: Google_Places_API_Scraper/google_places.py
Dependencies: requests
"""

import time
import requests
import json
from typing import Dict, List, Any, Optional


class GooglePlacesAPI:
    """
    Client for interacting with Google Places API to search for and retrieve
    place details.
    """
    
    BASE_URL = "https://maps.googleapis.com/maps/api"
    PLACES_TEXT_SEARCH_URL = f"{BASE_URL}/place/textsearch/json"
    PLACES_NEARBY_SEARCH_URL = f"{BASE_URL}/place/nearbysearch/json"
    PLACE_DETAILS_URL = f"{BASE_URL}/place/details/json"
    
    # Center coordinates for Aargau, Switzerland
    AARGAU_LAT = 47.3887
    AARGAU_LNG = 8.0558
    
    def __init__(self, api_key: str) -> None:
        """
        Initialize the Google Places API client.
        
        Args:
            api_key: Google API key with Places API enabled
        """
        self.api_key = api_key
        # Mask the API key for debug printing
        self.masked_key = api_key[:4] + '****' + api_key[-4:] if len(api_key) > 8 else '****'
        print(f"Initialized Google Places API client with key: {self.masked_key}")
    
    def text_search(self, keyword: str, region: str) -> List[Dict[str, Any]]:
        """
        Perform a text search using the Google Places API.
        
        Args:
            keyword: Search terms (e.g., "farm shops")
            region: Target region to search within
            
        Returns:
            List of place results
        """
        search_query = f"{keyword} in {region} Switzerland"
        print(f"Text search query: '{search_query}'")
        all_results = []
        next_page_token = None
        
        while True:
            params = {
                "query": search_query,
                "key": self.api_key
            }
            
            if next_page_token:
                params["pagetoken"] = next_page_token
            
            url = self.PLACES_TEXT_SEARCH_URL
            print(f"Making API request to: {url} with query: '{search_query}'")
            
            response = requests.get(url, params=params)
            data = response.json()
            
            print(f"API response status: {response.status_code}")
            if response.status_code != 200:
                error_msg = data.get("error_message", "Unknown error")
                print(f"API error: {error_msg}")
                raise Exception(f"Google Places API error: {error_msg}")
            
            results = data.get("results", [])
            print(f"Got {len(results)} results from this page")
            
            if len(results) == 0:
                print("API response details: " + json.dumps(data, indent=2))
            
            all_results.extend(results)
            
            # Check if there are more pages of results
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                print("No next_page_token, stopping pagination")
                break
                
            print(f"Got next_page_token, will fetch next page after delay")
            # Google requires a delay before using the next_page_token
            time.sleep(2)
        
        print(f"Total results from text search: {len(all_results)}")
        
        # Fetch detailed information for each place
        detailed_results = []
        for place in all_results:
            place_id = place.get("place_id")
            if place_id:
                print(f"Fetching details for place: {place.get('name', 'Unknown')} (ID: {place_id})")
                place_details = self.get_place_details(place_id)
                if place_details:
                    detailed_results.append(place_details)
        
        return detailed_results
    
    def nearby_search(self, keyword: str, radius: int = 50000) -> List[Dict[str, Any]]:
        """
        Perform a nearby search using the Google Places API.
        
        Args:
            keyword: Search terms (e.g., "farm shops")
            radius: Search radius in meters
            
        Returns:
            List of place results
        """
        print(f"Nearby search for '{keyword}' with radius {radius}m around {self.AARGAU_LAT},{self.AARGAU_LNG}")
        all_results = []
        next_page_token = None
        
        while True:
            params = {
                "keyword": keyword,
                "location": f"{self.AARGAU_LAT},{self.AARGAU_LNG}",
                "radius": radius,
                "key": self.api_key
            }
            
            if next_page_token:
                params["pagetoken"] = next_page_token
            
            url = self.PLACES_NEARBY_SEARCH_URL
            print(f"Making API request to: {url}")
            
            response = requests.get(url, params=params)
            data = response.json()
            
            print(f"API response status: {response.status_code}")
            if response.status_code != 200:
                error_msg = data.get("error_message", "Unknown error")
                print(f"API error: {error_msg}")
                raise Exception(f"Google Places API error: {error_msg}")
            
            results = data.get("results", [])
            print(f"Got {len(results)} results from this page")
            
            if len(results) == 0:
                print("API response details: " + json.dumps(data, indent=2))
            
            all_results.extend(results)
            
            # Check if there are more pages of results
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                print("No next_page_token, stopping pagination")
                break
                
            print(f"Got next_page_token, will fetch next page after delay")
            # Google requires a delay before using the next_page_token
            time.sleep(2)
        
        print(f"Total results from nearby search: {len(all_results)}")
        
        # Fetch detailed information for each place
        detailed_results = []
        for place in all_results:
            place_id = place.get("place_id")
            if place_id:
                print(f"Fetching details for place: {place.get('name', 'Unknown')} (ID: {place_id})")
                place_details = self.get_place_details(place_id)
                if place_details:
                    detailed_results.append(place_details)
        
        return detailed_results
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed information for a specific place.
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Dictionary containing place details or None if failed
        """
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,place_id,types,website,url,opening_hours,address_components",
            "key": self.api_key
        }
        
        print(f"Fetching details for place_id: {place_id}")
        response = requests.get(self.PLACE_DETAILS_URL, params=params)
        data = response.json()
        
        if response.status_code != 200:
            print(f"Error fetching details for place {place_id}: {data.get('error_message', 'Unknown error')}")
            return None
        
        place_data = data.get("result")
        if place_data:
            print(f"Successfully retrieved details for {place_data.get('name', 'Unknown')}")
            # Print first few address components for debugging
            address_components = place_data.get("address_components", [])
            if address_components:
                print(f"Address components: {[comp.get('long_name', '') for comp in address_components[:3]]}...")
        else:
            print(f"No result data for place_id: {place_id}")
        
        return place_data
    
    def filter_by_region(self, places: List[Dict[str, Any]], region: str) -> List[Dict[str, Any]]:
        """
        Filter places to only include those in the specified region.
        
        Args:
            places: List of place details
            region: Region name to filter by (e.g., "Aargau")
            
        Returns:
            Filtered list of places
        """
        print(f"Filtering {len(places)} places to only include those in '{region}'")
        region_lower = region.lower()
        filtered_places = []
        
        for place in places:
            # Check if place is in the target region
            address_components = place.get("address_components", [])
            
            is_in_region = False
            for component in address_components:
                comp_name = component.get("long_name", "").lower()
                if region_lower in comp_name:
                    is_in_region = True
                    print(f"Found place in {region}: {place.get('name')} (Component: {component.get('long_name')})")
                    break
            
            if is_in_region:
                filtered_places.append(place)
        
        print(f"After filtering, {len(filtered_places)} places remain")
        return filtered_places 