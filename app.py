import streamlit as st
from components.historical_form import display_historical_form
from components.simulated_form import display_simulated_form
from utils.api import API_URL

st.set_page_config(
    page_title="Prop Trading Simulator",
    page_icon="📈",
    layout="wide"
)

def main():
    st.title("Prop Trading Account Simulator")
    
    # Create tabs for different simulation modes
    tab1, tab2 = st.tabs(["Simulated Parameters", "Historical Data"])
    
    with tab1:
        display_simulated_form()
        
    with tab2:
        display_historical_form()

if __name__ == "__main__":
    main()

