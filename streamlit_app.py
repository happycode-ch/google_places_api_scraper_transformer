"""
AI-driven development file
Purpose: Streamlit frontend for viewing and filtering farm shop data
Module: Google_Places_API_Scraper/streamlit_app.py
Dependencies: streamlit, pandas, json, pydeck
"""

import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from pathlib import Path
from typing import Dict, List, Any, Optional


class FarmShopViewer:
    """
    Streamlit viewer for farm shop data collected from Google Places API.
    """
    
    def __init__(self) -> None:
        """Initialize the FarmShopViewer."""
        self.data = None
        self.df = None
    
    def load_data(self, file_path: str) -> None:
        """
        Load farm shop data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
        # Convert to pandas DataFrame for easier filtering and display
        self.df = self._prepare_dataframe()
    
    def _prepare_dataframe(self) -> pd.DataFrame:
        """
        Prepare a pandas DataFrame from the loaded data.
        
        Returns:
            DataFrame with farm shop data
        """
        if not self.data:
            return pd.DataFrame()
            
        # For raw data format
        if self.data and isinstance(self.data[0], dict) and "geometry" in self.data[0]:
            df = pd.json_normalize(self.data)
            
            # Rename location columns if they exist
            if 'geometry.location.lat' in df.columns and 'geometry.location.lng' in df.columns:
                df.rename(columns={
                    'geometry.location.lat': 'latitude',
                    'geometry.location.lng': 'longitude'
                }, inplace=True)
                
        # For cleaned data format
        else:
            df = pd.DataFrame(self.data)
            
        return df
    
    def run_app(self) -> None:
        """Run the Streamlit application."""
        st.title("Farm Shop Viewer")
        st.write("View and filter farm shops in Canton Aargau, Switzerland")
        
        # File selector
        data_path = st.sidebar.text_input(
            "Path to JSON data file", 
            value="data/aargau_raw.json"
        )
        
        try:
            self.load_data(data_path)
            
            if self.df is None or self.df.empty:
                st.warning("No data loaded. Please check the file path.")
                return
                
            # Filter controls
            st.sidebar.header("Filters")
            
            # Filter by website presence
            has_website = st.sidebar.checkbox("Only shops with websites")
            if has_website:
                if 'website' in self.df.columns:
                    self.df = self.df[self.df['website'].notna() & (self.df['website'] != '')]
            
            # Display data table
            st.subheader("Farm Shops")
            
            # Select display columns
            display_cols = []
            
            # Common columns between raw and cleaned data
            if 'name' in self.df.columns:
                display_cols.append('name')
                
            if 'formatted_address' in self.df.columns:
                display_cols.append('formatted_address')
            elif 'address' in self.df.columns:
                display_cols.append('address')
                
            if 'latitude' in self.df.columns and 'longitude' in self.df.columns:
                display_cols.extend(['latitude', 'longitude'])
                
            if 'website' in self.df.columns:
                display_cols.append('website')
                
            # Display table with selected columns
            st.dataframe(self.df[display_cols])
            
            # Display map if coordinates are available
            if 'latitude' in self.df.columns and 'longitude' in self.df.columns:
                self._display_map()
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def _display_map(self) -> None:
        """Display the farm shops on a map using PyDeck."""
        st.subheader("Map View")
        
        # Create data for map
        map_data = self.df[['latitude', 'longitude', 'name']]
        map_data = map_data.dropna(subset=['latitude', 'longitude'])
        
        if map_data.empty:
            st.info("No location data available for map display")
            return
            
        # Calculate map center
        center_lat = map_data['latitude'].mean()
        center_lng = map_data['longitude'].mean()
        
        # Create PyDeck layer
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=map_data,
            get_position=['longitude', 'latitude'],
            get_radius=250,
            get_fill_color=[180, 0, 200, 140],
            pickable=True,
            auto_highlight=True
        )
        
        # Set the viewport location
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lng,
            zoom=9,
            pitch=0
        )
        
        # Create the PyDeck chart
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v9',
            tooltip={
                'text': '{name}'
            }
        )
        
        # Display the map
        st.pydeck_chart(deck)


if __name__ == '__main__':
    viewer = FarmShopViewer()
    viewer.run_app() 