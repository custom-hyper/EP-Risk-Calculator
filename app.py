import streamlit as st
import pandas as pd
# from sqlalchemy import create_engine



# Streamlit app title
st.title("EP Risk Reward Table")

# Fetch data from the CSV file
data = pd.read_csv(r"filtered_markets.csv")

# Display the data in the Streamlit app
if not data.empty:
    st.write(f"Results from the CSV file:")
    st.dataframe(data)
