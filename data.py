import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Indian Stock Explosion Predictor", layout="wide")
st.title("🚀 Indian Stock Explosion Predictor")

@st.cache_data(ttl=30)  # Cache data for 30 seconds to avoid excessive API calls
def fetch_nse_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    return hist

# Function to fetch market news
def get_news(ticker):
    api_url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&apiKey=0ba785010ef34b33b31eb4def71e51b4"
    response = requests.get(api_url)
    news_data = response.json()
    
    articles = news_data.get("articles", [])
    headlines = [article["title"] for article in articles[:5]]
    return headlines

# Function to calculate target price
def calculate_target_price(price, change, volume):
    fib_multiplier = 1.618
    volatility_factor = 1 + (volume / 10000000)
    return round(price * (1 + ((change / 100) * fib_multiplier * volatility_factor)), 2)

# Function to calculate stop-loss
def calculate_stop_loss(price, change):
    stop_loss_factor = 0.95 if change > 8 else 0.90
    return round(price * stop_loss_factor, 2)

# Fetch all NSE stocks
def get_all_nse_stocks():
    nse_tickers = pd.read_html("https://www.nseindia.com/market-data/live-equity-market")[0]
    return nse_tickers["SYMBOL"].tolist()

nse_stocks = [ticker + ".NS" for ticker in get_all_nse_stocks()]

# Function to analyze multiple stocks
def analyze_market():
    results = []
    for ticker in nse_stocks:
        stock_data = fetch_nse_data(ticker)
        
        if stock_data.empty:
            continue
        
        latest_close = stock_data["Close"].iloc[-1]
        volume = stock_data["Volume"].iloc[-1]
        change = ((latest_close - stock_data["Close"].iloc[-2]) / stock_data["Close"].iloc[-2]) * 100
        
        if change > 5 and volume > 500000:
            target_price = calculate_target_price(latest_close, change, volume)
            stop_loss_price = calculate_stop_loss(latest_close, change)
            trade_decision = "✅ Strong Buy" if change > 8 else "⚠ Moderate Buy"
            reasons = get_news(ticker)
            
            results.append({
                "Stock": ticker, "Current Price": latest_close, "24h Change (%)": round(change, 2),
                "Volume": volume, "Target Price": target_price,
                "Stop Loss Price": stop_loss_price, "Trade Decision": trade_decision,
                "Reasons for Movement": ", ".join(reasons)
            })
    return results

# Fetch and analyze market data
data = analyze_market()
if data:
    df = pd.DataFrame(data)
    st.subheader("📈 Stocks Likely to Explode Soon")
    st.dataframe(df)
else:
    st.info("No potential explosive stocks detected right now.")

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun()
