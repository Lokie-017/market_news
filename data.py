import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor with AI Insights")

@st.cache_data(ttl=30)  # Cache data for 30 seconds to reduce API calls
def fetch_coindcx_data():
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [coin for coin in data if coin['market'].endswith('INR')]  # Filter INR pairs
    else:
        return []

# Placeholder function to integrate InciteAI insights
def fetch_inciteai_predictions(symbol):
    # Replace with actual InciteAI API call
    ai_url = f"https://api.inciteai.com/predict?symbol={symbol}"
    response = requests.get(ai_url)
    
    if response.status_code == 200:
        ai_data = response.json()
        return ai_data.get("prediction", "Neutral"), ai_data.get("confidence", 50)
    else:
        return "Neutral", 50

def calculate_target_price(price, change, volume):
    fib_multiplier = 1.618
    volatility_factor = 1 + (volume / 10000000)
    return round(price * (1 + ((change / 100) * fib_multiplier * volatility_factor)), 2)

def calculate_stop_loss(price, change):
    stop_loss_factor = 0.95 if change > 8 else 0.90
    return round(price * stop_loss_factor, 2)

def calculate_volatility(change, volume):
    volatility = abs(change) * (1 + (volume / 10000000))  
    return round(volatility, 2)

def analyze_market(data):
    potential_explosions = []
    for coin in data:
        try:
            symbol = coin.get('market', 'N/A')
            price = float(coin.get('last_price', 0))
            volume = float(coin.get('volume', 0))
            change = float(coin.get('change_24_hour', 0))

            if change > 5 and volume > 500000:
                target_price = calculate_target_price(price, change, volume)
                stop_loss_price = calculate_stop_loss(price, change)
                volatility = calculate_volatility(change, volume)
                ai_prediction, ai_confidence = fetch_inciteai_predictions(symbol)

                if volatility > 20:
                    trade_decision = "🔥 High Volatility - Enter with Caution"
                elif volatility > 10:
                    trade_decision = "✅ Strong Buy"
                else:
                    trade_decision = "⚠ Moderate Buy"

                potential_explosions.append({
                    "Symbol": symbol, "Price": price, "24h Change (%)": change,
                    "Volume": volume, "Volatility (%)": volatility,
                    "Target Price": target_price, "Stop Loss Price": stop_loss_price, 
                    "Trade Decision": trade_decision, "AI Prediction": ai_prediction,
                    "AI Confidence (%)": ai_confidence
                })
        except ValueError:
            continue
    return potential_explosions

# Fetch and display data
data = fetch_coindcx_data()
if data:
    analyzed_data = analyze_market(data)
    if analyzed_data:
        df = pd.DataFrame(analyzed_data)
        st.subheader("📈 Cryptos Likely to Explode Soon (AI Enhanced)")
        st.dataframe(df)
    else:
        st.info("No potential explosive cryptos detected right now.")
else:
    st.error("Failed to retrieve data. Please check API access.")

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun()
