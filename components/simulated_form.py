import streamlit as st
from components.core_parameters import display_core_parameters
from components.results import display_results
from utils.api import run_simulation

def display_simulated_form():
    st.markdown("### Simulate with Strategy Parameters")
    st.markdown("Enter your trading strategy parameters for the simulation")

    # Strategy parameters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_trades = st.number_input(
            "Average Trades per Day",
            min_value=0.1,
            value=10.0,
            step=0.1,
            key="simulated_avg_trades"
        )
    
    with col2:
        stop_loss = st.number_input(
            "Stop Loss (Ticks)",
            min_value=1,
            value=40,
            step=1,
            key="simulated_stop_loss"
        )
    
    with col3:
        take_profit = st.number_input(
            "Take Profit (Ticks)",
            min_value=1,
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

    if st.button("Run Simulation", type="primary", key="simulated_run_button"):
        # Ensure all numeric values are properly typed
        config = {
            "iterations": int(params["iterations"]),
            "max_simulation_days": int(params["max_simulation_days"]),
            "account_type": str(params["account_type"]),
            "multiplier": float(params["multiplier"]),
            "round_trip_cost": float(params["round_trip_cost"]),
            "histogram": True,
            "condition_end_state": str(params["condition_end_state"]),
            "max_payouts": 12,
            "avg_trades_per_day": float(avg_trades),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "win_percentage": float(win_percentage)
        }

        with st.spinner("Running simulation..."):
            results = run_simulation(config)
            if results:
                display_results(results)
