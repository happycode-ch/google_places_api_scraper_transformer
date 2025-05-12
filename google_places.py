"""
AI-driven development file
Purpose: Google Places API interaction module for farm shop data retrieval
Module: Google_Places_API_Scraper/google_places.py
Dependencies: requests
"""

import time
import requests
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
        all_results = []
        next_page_token = None
        
        while True:
            params = {
                "query": search_query,
                "key": self.api_key
            }
            
            if next_page_token:
                params["pagetoken"] = next_page_token
            
            response = requests.get(self.PLACES_TEXT_SEARCH_URL, params=params)
            data = response.json()
            
            if response.status_code != 200:
                error_msg = data.get("error_message", "Unknown error")
                raise Exception(f"Google Places API error: {error_msg}")
            
            results = data.get("results", [])
            all_results.extend(results)
            
            # Check if there are more pages of results
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
                
            # Google requires a delay before using the next_page_token
            time.sleep(2)
        
        # Fetch detailed information for each place
        detailed_results = []
        for place in all_results:
            place_id = place.get("place_id")
            if place_id:
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
            
            response = requests.get(self.PLACES_NEARBY_SEARCH_URL, params=params)
            data = response.json()
            
            if response.status_code != 200:
                error_msg = data.get("error_message", "Unknown error")
                raise Exception(f"Google Places API error: {error_msg}")
            
            results = data.get("results", [])
            all_results.extend(results)
            
            # Check if there are more pages of results
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
                
            # Google requires a delay before using the next_page_token
            time.sleep(2)
        
        # Fetch detailed information for each place
        detailed_results = []
        for place in all_results:
            place_id = place.get("place_id")
            if place_id:
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
        
        response = requests.get(self.PLACE_DETAILS_URL, params=params)
        data = response.json()
        
        if response.status_code != 200:
            print(f"Error fetching details for place {place_id}: {data.get('error_message', 'Unknown error')}")
            return None
        
        return data.get("result")
    
    def filter_by_region(self, places: List[Dict[str, Any]], region: str) -> List[Dict[str, Any]]:
        """
        Filter places to only include those in the specified region.
        
        Args:
            places: List of place details
            region: Region name to filter by (e.g., "Aargau")
            
        Returns:
            Filtered list of places
        """
        filtered_places = []
        
        for place in places:
            # Check if place is in the target region
            address_components = place.get("address_components", [])
            
            is_in_region = False
            for component in address_components:
                if region.lower() in component.get("long_name", "").lower():
                    is_in_region = True
                    break
            
            if is_in_region:
                filtered_places.append(place)
        
        return filtered_places 