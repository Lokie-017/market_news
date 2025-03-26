import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Stock Breakout Predictor", layout="wide")
st.title("📈 Stock Breakout Predictor")

@st.cache_data(ttl=300)
def get_nse_stocks():
    try:
        nse_symbols = pd.read_html("https://www.nseindia.com/market-data/live-equity-market")[0]["Symbol"].tolist()
        return [symbol + ".NS" for symbol in nse_symbols if isinstance(symbol, str)]
    except:
        return []

timeframe = "1mo"
nse_stocks = get_nse_stocks()

@st.cache_data(ttl=300)
def fetch_stock_data(symbol, period):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        return df if not df.empty else None
    except Exception as e:
        return None

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

for stock_symbol in nse_stocks:
    df = fetch_stock_data(stock_symbol, timeframe)
    if df is not None:
        df = calculate_indicators(df)
        stock_analysis = analyze_stock(df)
        stock_analysis["Symbol"] = stock_symbol
        if stock_analysis["Trade Decision"] == "✅ Strong Buy":
            breakout_stocks.append(stock_analysis)

if breakout_stocks:
    st.dataframe(pd.DataFrame(breakout_stocks))
else:
    st.info("No breakout stocks detected right now.")

time.sleep(60)
st.rerun()
