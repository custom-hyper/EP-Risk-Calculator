import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection parameters for SQLite
db_url = r'C:\Users\charl\OneDrive\workspace\algo\MEXC.db'  # Ensure this path is correct
engine = create_engine(f'sqlite:///{db_url}')

# Streamlit app title
st.title("EP Risk Reward Table")

# Fetch the most recent date from the EP_screen table
most_recent_date_query = "SELECT MAX(date) FROM EP_screen"
most_recent_date = pd.read_sql(most_recent_date_query, engine).iloc[0, 0]

# Fetch data for the most recent date
query = f"SELECT * FROM EP_screen WHERE date = '{most_recent_date}'"
data = pd.read_sql(query, engine)

# Display the data in the Streamlit app
if not data.empty:
    st.write(f"Results for the most recent date: {most_recent_date}")
    st.dataframe(data)
else:
    st.write("No data available for the most recent date.")
