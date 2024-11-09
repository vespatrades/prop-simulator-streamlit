import streamlit as st
import plotly.io as pio
import json

def display_results(results):
    """Display simulation results with a nice layout"""
    
    # Create three columns for statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Balance Statistics")
        st.metric("Mean Balance", f"${results['mean_balance']:.2f}")
        st.metric("Median Balance", f"${results['median_balance']:.2f}")
        st.metric("Standard Deviation", f"${results['std_dev']:.2f}")
        st.metric("Positive Balance", f"{results['positive_balance_percentage']:.1f}%")

    with col2:
        st.markdown("### Simulation Statistics")
        st.metric("Mean Days", f"{results['mean_days']:.1f}")
        st.metric("MAD", f"${results['mad']:.2f}")
        st.metric("IQR", f"${results['iqr']:.2f}")
        st.metric("MAD Median", f"${results['mad_median']:.2f}")

    with col3:
        st.markdown("### End States")
        for state, percentage in results['end_state_percentages'].items():
            st.metric(state, f"{percentage:.1f}%")

    # Display histogram if available
    if 'histogram_plotly_json' in results and results['histogram_plotly_json']:
        st.markdown("### Distribution of Final Account Balances")
        try:
            fig_json = json.loads(results['histogram_plotly_json'])
            st.plotly_chart(fig_json, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying histogram: {str(e)}")

