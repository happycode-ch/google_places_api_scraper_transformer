"""
AI-driven development file
Purpose: Export functionality for farm shop data to various formats
Module: Google_Places_API_Scraper/export.py
Dependencies: json, csv, pandas
"""

import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path


class DataExporter:
    """
    Export farm shop data to various formats (JSON, CSV).
    """
    
    def __init__(self) -> None:
        """Initialize the DataExporter."""
        pass
    
    def export_json(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export data to a JSON file.
        
        Args:
            data: List of dictionaries to export
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def export_csv(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export data to a CSV file.
        
        This method flattens nested structures to create a tabular format
        suitable for Excel and similar tools.
        
        Args:
            data: List of dictionaries to export
            output_path: Path to save the CSV file
        """
        # Convert to pandas DataFrame
        df = pd.json_normalize(data)
        
        # Handle specific nested structures
        if 'geometry.location.lat' in df.columns and 'geometry.location.lng' in df.columns:
            df.rename(columns={
                'geometry.location.lat': 'latitude', 
                'geometry.location.lng': 'longitude'
            }, inplace=True)
        
        # Convert opening_hours to a flattened string representation
        if 'opening_hours.weekday_text' in df.columns:
            df['opening_hours'] = df['opening_hours.weekday_text'].apply(
                lambda x: '; '.join(x) if isinstance(x, list) else ''
            )
            df.drop('opening_hours.weekday_text', axis=1, inplace=True)
        
        # Handle address components
        if 'address_components' in df.columns:
            # Extract relevant address component types
            for component_type in ['locality', 'administrative_area_level_1', 'postal_code', 'country']:
                df[component_type] = df['address_components'].apply(
                    lambda comps: self._extract_address_component(comps, component_type) 
                    if isinstance(comps, list) else ''
                )
            
            # Remove the original nested column
            df.drop('address_components', axis=1, inplace=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False, encoding='utf-8')
    
    def _extract_address_component(
        self, 
        components: List[Dict[str, Any]], 
        component_type: str
    ) -> str:
        """
        Extract a specific address component by type.
        
        Args:
            components: List of address components
            component_type: The type of component to extract
            
        Returns:
            The long_name of the matching component, or empty string if not found
        """
        for component in components:
            if component_type in component.get('types', []):
                return component.get('long_name', '')
        return '' 