# components/historical_form.py
import streamlit as st
import pandas as pd
import logging
from components.core_parameters import display_core_parameters
from components.results import display_results
from utils.api import run_simulation

logger = logging.getLogger(__name__)

def display_historical_form():
    st.markdown("### Simulate with Historical Data")
    st.markdown("Upload your historical trading data in CSV format")

    # File uploader
    csv_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="CSV format: DateTime, Return, Max Opposite Excursion",
        key="historical_csv_upload"
    )

    # Core parameters
    params = display_core_parameters(prefix="historical_")

    if st.button("Run Simulation", type="primary", key="historical_run_button"):
        if csv_file is None:
            st.error("Please upload a CSV file")
            return

        try:
            # Read CSV file
            df = pd.read_csv(csv_file)

            # Display the first few rows for verification
            st.write("Preview of uploaded data:")
            st.write(df.head())

            # Strip whitespace from column names
            df.columns = df.columns.str.strip()

            # Check columns
            required_columns = ["DateTime", "Return", "Max Opposite Excursion"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                return

            # Basic data validation
            if df.empty:
                st.error("The CSV file is empty")
                return

            # Reset file pointer for sending
            csv_file.seek(0)

            # Prepare configuration
            config = {
                "iterations": int(params["iterations"]),
                "max_simulation_days": int(params["max_simulation_days"]),
                "account_type": str(params["account_type"]),
                "multiplier": float(params["multiplier"]),
                "round_trip_cost": float(params["round_trip_cost"]),
                "histogram": True,
                "condition_end_state": str(params["condition_end_state"]),
                "max_payouts": 12
            }

            with st.spinner("Running simulation..."):
                results = run_simulation(config, csv_file.getvalue())
                if results:
                    display_results(results)

        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty")
        except pd.errors.ParserError as e:
            st.error(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")

