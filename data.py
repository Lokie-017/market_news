import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Indian Stock Explosion Predictor", layout="wide")
st.title("🚀 Indian Stock Explosion Predictor")

@st.cache_data(ttl=300)  # Cache data for 5 minutes to reduce API calls
def fetch_nse_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    time.sleep(1)  # Pause to avoid rate limiting
    return hist

@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_all_nse_stocks():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return df["SYMBOL"].tolist()

nse_stocks = [ticker + ".NS" for ticker in get_all_nse_stocks()]

def analyze_market():
    results = []
    for ticker in nse_stocks[:50]:  # Limit requests to avoid rate limiting
        stock_data = fetch_nse_data(ticker)
        
        if stock_data.empty:
            continue
        
        latest_close = stock_data["Close"].iloc[-1]
        volume = stock_data["Volume"].iloc[-1]
        change = ((latest_close - stock_data["Close"].iloc[-2]) / stock_data["Close"].iloc[-2]) * 100
        
        if change > 5 and volume > 500000:
            results.append({
                "Stock": ticker, "Current Price": latest_close, "24h Change (%)": round(change, 2),
                "Volume": volume
            })
    return results

data = analyze_market()
if data:
    df = pd.DataFrame(data)
    st.subheader("📈 Stocks Likely to Explode Soon")
    st.dataframe(df)
else:
    st.info("No potential explosive stocks detected right now.")

time.sleep(30)
st.rerun()
