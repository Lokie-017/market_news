import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor")

@st.cache_data(ttl=30)  # Cache data for 30 seconds to reduce API calls
def fetch_coindcx_data():
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {coin['market']: coin for coin in data if coin['market'].endswith('INR')}  # Convert to dict for easy lookup
    else:
        return {}

def calculate_target_price(price, change, volume):
    fib_multiplier = 1.618
    volatility_factor = 1 + (volume / 10000000)
    return round(price * (1 + ((change / 100) * fib_multiplier * volatility_factor)), 2)

def calculate_stop_loss(price, change):
    stop_loss_factor = 0.95 if change > 8 else 0.90
    return round(price * stop_loss_factor, 2)

def analyze_market(data):
    potential_explosions = []
    for symbol, coin in data.items():
        try:
            price = float(coin.get('last_price', 0))
            volume = float(coin.get('volume', 0))
            change = float(coin.get('change_24_hour', 0))

            if change > 5 and volume > 500000:
                target_price = calculate_target_price(price, change, volume)
                stop_loss_price = calculate_stop_loss(price, change)

                trade_decision = "✅ Strong Buy" if change > 10 else "⚠ Moderate Buy"

                potential_explosions.append({
                    "Symbol": symbol, "Price": price, "24h Change (%)": change,
                    "Volume": volume, "Target Price": target_price, "Stop Loss Price": stop_loss_price, 
                    "Trade Decision": trade_decision
                })
        except ValueError:
            continue

    return pd.DataFrame(potential_explosions) if potential_explosions else pd.DataFrame()

# Fetch data
data = fetch_coindcx_data()

# Initialize session state for tracking positions
if "positions" not in st.session_state:
    st.session_state.positions = {}

if "positionsON" not in st.session_state:
    st.session_state.positionsON = pd.DataFrame(columns=["Symbol", "Entry Time", "Price", "Volume", "Target Price", "Stop Loss Price", "Status", "Suggestion"])

if data:
    df = analyze_market(data)
    
    if not df.empty:
        st.subheader("📈 Cryptos Likely to Explode Soon")

        # Add checkbox column dynamically
        positions = []
        for symbol in df["Symbol"]:
            position_taken = st.checkbox(f"📌 {symbol}", st.session_state.positions.get(symbol, False), key=symbol)
            positions.append(position_taken)

            # If position is taken & not already stored, add it to positionsON
            if position_taken and not st.session_state.positions.get(symbol, False):
                coin_data = df[df["Symbol"] == symbol].iloc[0]
                new_entry = pd.DataFrame([{
                    "Symbol": symbol, 
                    "Entry Time": datetime.now(), 
                    "Price": coin_data["Price"],
                    "Volume": coin_data["Volume"],
                    "Target Price": coin_data["Target Price"],
                    "Stop Loss Price": coin_data["Stop Loss Price"],
                    "Status": "Holding",
                    "Suggestion": "Hold"
                }])
                st.session_state.positionsON = pd.concat([st.session_state.positionsON, new_entry], ignore_index=True)

            st.session_state.positions[symbol] = position_taken

        # Add positions column
        df["Took Position"] = positions

        # Show updated DataFrame
        st.dataframe(df)

        # Display Active Positions
        st.subheader("📊 Positions Tracking")
        if not st.session_state.positionsON.empty:
            for index, row in st.session_state.positionsON.iterrows():
                if row["Symbol"] in data:
                    current_price = float(data[row["Symbol"]]["last_price"])
                    entry_price = row["Price"]
                    target_price = row["Target Price"]
                    stop_loss = row["Stop Loss Price"]

                    # Determine if should hold or sell
                    if current_price >= target_price:
                        status = "✅ Target Hit"
                        suggestion = "Sell"
                    elif current_price <= stop_loss:
                        status = "🚨 Stop Loss Hit"
                        suggestion = "Sell"
                    else:
                        status = "📈 Holding"
                        suggestion = "Hold"

                    st.session_state.positionsON.at[index, "Status"] = status
                    st.session_state.positionsON.at[index, "Suggestion"] = suggestion

            st.dataframe(st.session_state.positionsON)

    else:
        st.info("No potential explosive cryptos detected right now.")
else:
    st.error("Failed to retrieve data. Please check API access.")

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun()
