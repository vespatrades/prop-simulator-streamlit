# utils/api.py
import requests
import json
import logging
from typing import Dict, Any, Optional
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8080"

def run_simulation(
    config: Dict[str, Any],
    csv_file: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Run a simulation through the API
    """
    try:
        # Convert config to JSON string
        config_json = json.dumps(config)

        # Log the request for debugging
        logger.debug(f"Request config: {config_json}")

        # Prepare multipart form data
        files = {
            'config': ('config.json', config_json, 'application/json')
        }

        if csv_file is not None:
            files['csv_file'] = ('trades.csv', csv_file, 'text/csv')

        # Make the request
        response = requests.post(f"{API_URL}/simulate", files=files)

        # Check for errors
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the simulation server: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            st.error(f"Server response: {e.response.text}")
        logger.error(f"API error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        logger.error(f"General error: {str(e)}")
        return None

