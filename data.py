import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor")

@st.cache_data(ttl=30)
def fetch_coindcx_data():
    url = "https://api.coindcx.com/exchange/ticker"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return [coin for coin in response.json() if coin['market'].endswith('INR')]
    except requests.RequestException:
        return []

def calculate_target_price(price, change, volume):
    return round(price * (1 + ((change / 100) * 1.618 * (1 + (volume / 1e7)))), 2)

def calculate_stop_loss(price, change):
    return round(price * (0.95 if change > 8 else 0.90), 2)

def calculate_volatility(change, volume):
    return round(abs(change) * (1 + (volume / 1e7)), 2)

def get_trade_decision(volatility):
    if volatility > 20:
        return "🔥 High Volatility - Enter with Caution"
    elif volatility > 10:
        return "✅ Strong Buy"
    else:
        return "⚠ Moderate Buy"

def analyze_market(data):
    potential_explosions = []
    for coin in data:
        try:
            price = float(coin['last_price'])
            volume = float(coin['volume'])
            change = float(coin['change_24_hour'])
            
            if change > 5 and volume > 500000:
                volatility = calculate_volatility(change, volume)
                trade_decision = get_trade_decision(volatility)
                potential_explosions.append({
                    "Symbol": coin['market'], "Price": price, "24h Change (%)": change,
                    "Volume": volume, "Volatility (%)": volatility,
                    "Target Price": calculate_target_price(price, change, volume),
                    "Stop Loss Price": calculate_stop_loss(price, change),
                    "Trade Decision": trade_decision,
                    "Selected": False  # Checkbox state
                })
        except (ValueError, KeyError):
            continue
    return potential_explosions

# Fetch and display data
data = fetch_coindcx_data()
if data:
    analyzed_data = analyze_market(data)
    if analyzed_data:
        df = pd.DataFrame(analyzed_data)
        df["Selected"] = [st.checkbox("", key=i) for i in range(len(df))]
        df_selected = df[df["Selected"]]
        
        st.subheader("📈 Cryptos Likely to Explode Soon")
        st.dataframe(df)
        
        search_query = st.text_input("🔍 Search Crypto Symbol:")
        if search_query:
            searched_df = df[df["Symbol"].str.contains(search_query, case=False, na=False)]
            if not searched_df.empty:
                df_selected = pd.concat([df_selected, searched_df]).drop_duplicates().reset_index(drop=True)
            
        if not df_selected.empty:
            df_selected["Suggestion"] = df_selected["24h Change (%)"].apply(lambda x: "Hold" if x > 10 else "Sell")
            st.subheader("✅ Selected Cryptos")
            st.dataframe(df_selected)
    else:
        st.info("No potential explosive cryptos detected right now.")
else:
    st.error("Failed to retrieve data. Please check API access.")

st.experimental_rerun()  # Auto-refresh
