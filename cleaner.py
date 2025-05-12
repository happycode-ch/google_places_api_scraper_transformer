"""
AI-driven development file
Purpose: Clean and normalize Google Places API data for farm shops
Module: Google_Places_API_Scraper/cleaner.py
Dependencies: None
"""

from typing import Dict, List, Any, Optional


class DataCleaner:
    """
    Clean and normalize raw Google Places API data to match the required schema.
    """
    
    def __init__(self) -> None:
        """Initialize the DataCleaner."""
        pass
        
    def clean(self, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and normalize a list of place details.
        
        Args:
            places: List of raw place details from Google Places API
            
        Returns:
            List of cleaned and normalized place data
        """
        cleaned_places = []
        
        for place in places:
            cleaned_place = self._normalize_place(place)
            if cleaned_place:  # Only include if normalization succeeded
                cleaned_places.append(cleaned_place)
                
        return cleaned_places
    
    def _normalize_place(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize a single place to match the required schema.
        
        Args:
            place: Raw place details from Google Places API
            
        Returns:
            Normalized place data or None if essential data is missing
        """
        # Skip if essential data is missing
        if not place.get("name") or not place.get("formatted_address"):
            return None
            
        # Extract coordinates
        location = place.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        
        if not lat or not lng:
            return None
            
        # Extract and format opening hours
        opening_hours_dict = self._format_opening_hours(
            place.get("opening_hours", {}).get("weekday_text", [])
        )
        
        # Build normalized place data
        normalized_place = {
            "name": place.get("name", ""),
            "address": place.get("formatted_address", ""),
            "latitude": lat,
            "longitude": lng,
            "products": [],  # Would need additional data source or inference
            "organic_certified": self._infer_organic_status(place),
            "payment_methods": [],  # Would need additional data source
            "opening_hours": opening_hours_dict,
            "website": place.get("website", ""),
            "google_maps_url": place.get("url", "")
        }
        
        return normalized_place
    
    def _format_opening_hours(self, weekday_text: List[str]) -> Dict[str, str]:
        """
        Format opening hours from weekday text list to a dictionary.
        
        Args:
            weekday_text: List of strings like "Monday: 9:00 AM – 5:00 PM"
            
        Returns:
            Dictionary mapping day abbreviations to hours
        """
        hours_dict = {}
        
        # Day mappings
        day_mapping = {
            "monday": "Mon",
            "tuesday": "Tue",
            "wednesday": "Wed",
            "thursday": "Thu",
            "friday": "Fri",
            "saturday": "Sat",
            "sunday": "Sun"
        }
        
        for day_hours in weekday_text:
            if not day_hours or ":" not in day_hours:
                continue
                
            day, hours = day_hours.split(":", 1)
            day = day.strip().lower()
            hours = hours.strip()
            
            if day in day_mapping:
                hours_dict[day_mapping[day]] = hours
                
        return hours_dict
    
    def _infer_organic_status(self, place: Dict[str, Any]) -> bool:
        """
        Infer whether a farm shop is likely to be organic certified.
        
        This is a simple heuristic based on place name and types. For real data,
        you would need a more reliable source of organic certification status.
        
        Args:
            place: Raw place details
            
        Returns:
            Boolean indicating likely organic certification status
        """
        name = place.get("name", "").lower()
        types = [t.lower() for t in place.get("types", [])]
        
        # Look for organic indicators in name
        organic_keywords = ["bio", "organic", "öko", "naturkost", "demeter", "knospe"]
        for keyword in organic_keywords:
            if keyword in name:
                return True
                
        return False 