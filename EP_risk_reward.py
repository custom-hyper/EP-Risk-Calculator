import pandas as pd
import numpy as np  # Import numpy for using np.where
from sqlalchemy import create_engine

# Database connection parameters for SQLite
db_url = r'C:\Users\charl\OneDrive\workspace\algo\MEXC.db'  # Ensure this path is correct

# Create a database engine
engine = create_engine(f'sqlite:///{db_url}')

# Extract data from the premarket table
premarket_df = pd.read_sql('SELECT * FROM premarket', engine)

# Print the columns to check for 'close'
print(premarket_df.columns)  # Check the actual column names

# Function to calculate required columns for each market
def calculate_metrics(group):
    # Calculate the True Range
    group['prev_close'] = group['close'].shift(1)  # Shift close prices to get previous close
    group['true_range'] = np.maximum(
        group['high'] - group['low'],
        np.maximum(
            abs(group['high'] - group['prev_close']),
            abs(group['low'] - group['prev_close'])
        )
    )

    # Calculate the 30-day rolling ATR
    group['ATR'] = group['true_range'].rolling(window=14).mean()

    if 'close' in group.columns:
        group['current_vs_low'] = (group['close'] - group['low']) / group['low']  # Changed to use 'close'
    else:
        print(f"Column 'close' does not exist in the DataFrame for market: {group['market'].iloc[0]}.")
        group['current_vs_low'] = None  # Set to None or handle as needed

    group['three_times_atr'] = 3 * group['ATR']
    
    # Calculate 3ATR_risky_reward using np.where
    group['3ATR_risky_reward'] = np.where(
        (group['current_vs_low'].notnull()) & (group['current_vs_low'] != 0),
        group['three_times_atr'] / group['current_vs_low'],
        None
    )

    return group

# Apply the calculation function to each market group
premarket_df = premarket_df.groupby('market').apply(calculate_metrics)
print(premarket_df)

# Add today's date and rank the markets by 3ATR_risky_reward
premarket_df['date'] = pd.to_datetime('today').normalize()  # Add today's date
ranked_markets = premarket_df[['market', '3ATR_risky_reward', 'date']].dropna()  # Drop rows with NaN in 3ATR_risky_reward
ranked_markets = ranked_markets.sort_values(by='3ATR_risky_reward', ascending=False)  # Rank markets

print(ranked_markets)  # Display the ranked markets

# Convert the 'timestamp' column (UNIX timestamp in milliseconds) to date SQL format and store it in a new column called 'date'
premarket_df['date'] = pd.to_datetime(premarket_df['timestamp'] / 1000, unit='s').dt.date  # Convert 'timestamp' to date format

# Create the EP_screen table in the database
premarket_df.to_sql('EP_screen', engine, if_exists='replace', index=False)

# Display the ranked markets
print(ranked_markets)  # Display the ranked markets

# Save the filtered result to a CSV file
latest_date = ranked_markets['date'].max()  # Get the latest date
filtered_markets = ranked_markets[ranked_markets['date'] == latest_date].head(50)  # Filter for latest date and limit to 50 rows
print(filtered_markets)  # Display the filtered markets

filtered_markets.to_csv('filtered_markets.csv', index=False)  # Save as CSV
