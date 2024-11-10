import streamlit as st
from components.core_parameters import display_core_parameters
from components.results import display_results
from utils.api import run_simulation
from utils.security import (
    check_rate_limit,
    display_challenge,
    init_session_state,
    clear_session_state,
)


def display_simulated_form():
    # Initialize session state
    init_session_state()

    st.markdown("### Simulate with Strategy Parameters")
    st.markdown("Enter your trading strategy parameters for the simulation")

    # Strategy parameters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_trades = st.number_input(
            "Average Trades per Day",
            min_value=0.1,
            max_value=100.0,
            value=10.0,
            step=0.1,
            key="simulated_avg_trades"
        )

    with col2:
        stop_loss = st.number_input(
            "Stop Loss (Ticks)",
            min_value=1,
            max_value=1000,
            value=40,
            step=1,
            key="simulated_stop_loss"
        )

    with col3:
        take_profit = st.number_input(
            "Take Profit (Ticks)",
            min_value=1,
            max_value=1000,
            value=40,
            step=1,
            key="simulated_take_profit"
        )

    with col4:
        win_percentage = st.number_input(
            "Win Percentage",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=0.1,
            key="simulated_win_percentage"
        )

    # Core parameters
    params = display_core_parameters(prefix="simulated_")

    run_button = st.button("Run Simulation", type="primary", key="simulated_run_button")

    # Store parameters in session state when button is clicked
    if run_button:
        st.session_state.current_params = params
        st.session_state.current_strategy = {
            "avg_trades": avg_trades,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "win_percentage": win_percentage
        }

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

        try:
            # Prepare configuration
            params = st.session_state.current_params
            strategy = st.session_state.current_strategy

            if strategy is None:
                st.error("Strategy parameters not found. Please try again.")
                return

            config = {
                "iterations": int(params["iterations"]),
                "max_simulation_days": int(params["max_simulation_days"]),
                "account_type": str(params["account_type"]),
                "multiplier": float(params["multiplier"]),
                "round_trip_cost": float(params["round_trip_cost"]),
                "histogram": True,
                "condition_end_state": str(params["condition_end_state"]),
                "max_payouts": 12,
                "avg_trades_per_day": float(strategy["avg_trades"]),
                "stop_loss": float(strategy["stop_loss"]),
                "take_profit": float(strategy["take_profit"]),
                "win_percentage": float(strategy["win_percentage"])
            }

            # Run simulation
            with st.spinner("Running simulation..."):
                results = run_simulation(config)
                if results:
                    display_results(results)

        except Exception as e:
            st.error(f"Error running simulation: {str(e)}")

        finally:
            # Clear stored parameters after simulation
            clear_session_state()
