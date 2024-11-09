import streamlit as st
import pandas as pd
from components.core_parameters import display_core_parameters
from components.results import display_results
from utils.api import run_simulation

def display_historical_form():
    st.markdown("### Simulate with Historical Data")
    st.markdown("Upload your historical trading data in CSV format")

    # File uploader
    csv_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="CSV format: DateTime, Return, Max Opposite Excursion"
    )

    # Core parameters
    params = display_core_parameters()

    if st.button("Run Simulation", type="primary"):
        if csv_file is None:
            st.error("Please upload a CSV file")
            return

        try:
            # Verify CSV format
            df = pd.read_csv(csv_file)
            required_columns = ["DateTime", "Return", "Max Opposite Excursion"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV must contain columns: {', '.join(required_columns)}")
                return

            # Reset file pointer
            csv_file.seek(0)
            
            # Prepare configuration
            config = {
                "iterations": params["iterations"],
                "max_simulation_days": params["max_simulation_days"],
                "account_type": params["account_type"],
                "multiplier": params["multiplier"],
                "round_trip_cost": params["round_trip_cost"],
                "histogram": True,
                "condition_end_state": params["condition_end_state"],
                "max_payouts": 12
            }

            with st.spinner("Running simulation..."):
                results = run_simulation(config, csv_file.getvalue())
                if results:
                    display_results(results)

        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")

