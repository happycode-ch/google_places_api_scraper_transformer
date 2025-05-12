"""
AI-driven development file
Purpose: Geographic utilities for location filtering and validation
Module: Google_Places_API_Scraper/geo_utils.py
Dependencies: None
"""

from typing import Dict, List, Any, Tuple, Optional


class GeoUtils:
    """
    Geographic utilities for location filtering and validation.
    """
    
    # Approximate bounding box for Canton Aargau, Switzerland
    AARGAU_BOUNDS = {
        "north": 47.6229,  # Northern latitude
        "south": 47.1393,  # Southern latitude
        "east": 8.4651,    # Eastern longitude
        "west": 7.7075     # Western longitude
    }
    
    @staticmethod
    def is_point_in_aargau(lat: float, lng: float) -> bool:
        """
        Check if a coordinate point is within Canton Aargau's bounding box.
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            
        Returns:
            Boolean indicating if the point is within Aargau's bounds
        """
        bounds = GeoUtils.AARGAU_BOUNDS
        
        is_within_lat = bounds["south"] <= lat <= bounds["north"]
        is_within_lng = bounds["west"] <= lng <= bounds["east"]
        
        return is_within_lat and is_within_lng
    
    @staticmethod
    def filter_places_by_bounds(
        places: List[Dict[str, Any]], 
        bounds: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter places to only include those within specified bounding box.
        
        Args:
            places: List of place details
            bounds: Bounding box with north, south, east, west coordinates.
                   If None, uses Aargau bounds by default.
            
        Returns:
            Filtered list of places
        """
        if bounds is None:
            bounds = GeoUtils.AARGAU_BOUNDS
            
        filtered_places = []
        
        for place in places:
            location = place.get("geometry", {}).get("location", {})
            lat = location.get("lat")
            lng = location.get("lng")
            
            if lat is None or lng is None:
                continue
                
            is_within_lat = bounds["south"] <= lat <= bounds["north"]
            is_within_lng = bounds["west"] <= lng <= bounds["east"]
            
            if is_within_lat and is_within_lng:
                filtered_places.append(place)
                
        return filtered_places
    
    @staticmethod
    def get_aargau_grid_coordinates(
        grid_size: int = 5
    ) -> List[Tuple[float, float]]:
        """
        Generate a grid of coordinates covering Canton Aargau.
        
        This is useful for nearby searches to cover the entire canton
        by using multiple search origins.
        
        Args:
            grid_size: Number of points to generate in each dimension
            
        Returns:
            List of (latitude, longitude) coordinate tuples
        """
        bounds = GeoUtils.AARGAU_BOUNDS
        
        lat_step = (bounds["north"] - bounds["south"]) / (grid_size - 1)
        lng_step = (bounds["east"] - bounds["west"]) / (grid_size - 1)
        
        coordinates = []
        
        for i in range(grid_size):
            lat = bounds["south"] + (i * lat_step)
            
            for j in range(grid_size):
                lng = bounds["west"] + (j * lng_step)
                coordinates.append((lat, lng))
                
        return coordinates 