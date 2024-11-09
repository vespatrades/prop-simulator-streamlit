import streamlit as st
from config.accounts import ACCOUNT_TYPES, COMMON_MULTIPLIERS

# components/core_parameters.py

def display_core_parameters(prefix=""):
    """
    Display core parameters with unique keys for each component
    prefix: A string to make keys unique across different forms
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        # Account Type Selection
        account_options = []
        for provider, info in ACCOUNT_TYPES.items():
            account_options.extend(
                [(account["value"], f"{info['label']} - {account['label']}")
                 for account in info["accounts"]]
            )
        account_type = st.selectbox(
            "Account Type",
            options=[opt[0] for opt in account_options],
            format_func=lambda x: next(opt[1] for opt in account_options if opt[0] == x),
            index=2,  # Default to GT
            key=f"{prefix}account_type"  # Add unique key
        )

    with col2:
        # Round Trip Cost
        round_trip_cost = st.number_input(
            "Round Trip Cost",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key=f"{prefix}round_trip_cost"  # Add unique key
        )

    with col3:
        # Point Multiplier
        multiplier_options = [(m["value"], m["label"]) for m in COMMON_MULTIPLIERS]
        multiplier_options.append(("custom", "Custom Value..."))

        multiplier_selection = st.selectbox(
            "Point Multiplier",
            options=[opt[0] for opt in multiplier_options],
            format_func=lambda x: next(opt[1] for opt in multiplier_options if opt[0] == x),
            index=1,  # Default to NQ
            key=f"{prefix}multiplier_selection"  # Add unique key
        )

        if multiplier_selection == "custom":
            multiplier = st.number_input(
                "Custom Multiplier",
                min_value=1,
                value=20,
                step=1,
                key=f"{prefix}custom_multiplier"  # Add unique key
            )
        else:
            multiplier = multiplier_selection

    col4, col5, col6 = st.columns(3)

    with col4:
        # Iterations
        iterations = st.number_input(
            "Iterations",
            min_value=1000,
            value=10000,
            step=1000,
            key=f"{prefix}iterations"  # Add unique key
        )

    with col5:
        # Max Days
        max_days = st.number_input(
            "Max Days",
            min_value=1,
            value=365,
            step=1,
            key=f"{prefix}max_days"  # Add unique key
        )

    with col6:
        # End State Filter
        end_state = st.selectbox(
            "End State Filter",
            options=["All", "Busted", "TimeOut", "MaxPayouts"],
            index=0,
            key=f"{prefix}end_state"  # Add unique key
        )

    return {
        "account_type": account_type,
        "round_trip_cost": round_trip_cost,
        "multiplier": multiplier,
        "iterations": iterations,
        "max_simulation_days": max_days,
        "condition_end_state": end_state
    }

