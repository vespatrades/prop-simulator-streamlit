import requests
from typing import Dict, Any, Optional
import streamlit as st

API_URL = "http://localhost:8080"

def run_simulation(
    config: Dict[str, Any],
    csv_file: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Run a simulation through the API
    """
    try:
        files = {
            'config': ('config.json', str(config), 'application/json'),
        }
        
        if csv_file is not None:
            files['csv_file'] = ('trades.csv', csv_file, 'text/csv')
            
        response = requests.post(f"{API_URL}/simulate", files=files)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the simulation server: {str(e)}")
        return None

