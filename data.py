import streamlit as st
import pandas as pd
import time
import requests

st.set_page_config(page_title="Stock Breakout Predictor", layout="wide")
st.title("📈 Stock Breakout Predictor")

# Fetch stock data from Upstox API
def fetch_stock_data():
    url = "https://api.upstox.com/v2/market/quotes/NSE_EQ"
    headers = {"Authorization": "7d660bba-f2c8-4a6f-b7b0-a5c99b7e5380"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return []

def calculate_indicators(df):
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()
    df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean() / df["Close"].pct_change().rolling(14).std()))
    df["MACD"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

def analyze_stock(df):
    latest = df.iloc[-1]
    trade_decision = "❓ Neutral"
    
    if latest["Close"] > latest["SMA_50"] > latest["SMA_200"] and latest["RSI"] < 70 and latest["MACD"] > latest["Signal"]:
        trade_decision = "✅ Strong Buy"
    elif latest["RSI"] > 70:
        trade_decision = "⚠ Overbought - Wait"
    elif latest["Close"] < latest["SMA_50"]:
        trade_decision = "❌ Weak - Avoid"
    
    return {
        "Current Price": round(latest["Close"], 2),
        "50-Day SMA": round(latest["SMA_50"], 2),
        "200-Day SMA": round(latest["SMA_200"], 2),
        "RSI": round(latest["RSI"], 2),
        "MACD": round(latest["MACD"], 2),
        "Trade Decision": trade_decision
    }

st.subheader("🚀 Potential Breakout Stocks")
breakout_stocks = []

stock_data = fetch_stock_data()
for stock in stock_data:
    df = pd.DataFrame(stock["ohlc"])
    if not df.empty:
        df = calculate_indicators(df)
        stock_analysis = analyze_stock(df)
        stock_analysis["Symbol"] = stock["symbol"]
        if stock_analysis["Trade Decision"] == "✅ Strong Buy":
            breakout_stocks.append(stock_analysis)

if breakout_stocks:
    st.dataframe(pd.DataFrame(breakout_stocks))
else:
    st.info("No breakout stocks detected right now.")

time.sleep(60)
st.rerun()
