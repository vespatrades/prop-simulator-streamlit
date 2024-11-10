import streamlit as st
import logging
from components.core_parameters import display_core_parameters
from components.results import display_results
from utils.api import run_simulation
from utils.security import (
    validate_csv_file,
    check_rate_limit,
    display_challenge,
    init_session_state,
    clear_session_state,
)

logger = logging.getLogger(__name__)


def display_historical_form():
    # Initialize session state
    init_session_state()

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

    run_button = st.button("Run Simulation", type="primary", key="historical_run_button")

    # Store parameters in session state when button is clicked
    if run_button:
        st.session_state.current_params = params
        st.session_state.current_csv = csv_file

    # Check if we should run the simulation
    if (run_button or st.session_state.run_simulation) and st.session_state.current_params is not None:
        # Check rate limit
        if not check_rate_limit():
            st.error("Rate limit exceeded. Please wait before trying again.")
            return

        # Show challenge dialog if not verified
        if not st.session_state.get('challenge_verified'):
            display_challenge()
            return

        # Clear the run flag
        st.session_state.run_simulation = False

        csv_file = st.session_state.current_csv
        if csv_file is None:
            st.error("Please upload a CSV file")
            return

        try:
            # Validate CSV file
            is_valid, error_msg, df = validate_csv_file(csv_file)
            if not is_valid:
                st.error(error_msg)
                return

            # Reset file pointer for sending
            csv_file.seek(0)

            # Prepare configuration
            params = st.session_state.current_params
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

        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}")
            st.error(f"Error processing simulation: {str(e)}")

        finally:
            # Clear stored parameters after simulation
            clear_session_state()
