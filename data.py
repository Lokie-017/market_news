import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from textblob import TextBlob
import requests

# App Title
st.set_page_config(page_title="Invest AI - Smart Indian Stock Trading", layout="wide")
st.title("📈 Invest AI: Smart Trading Assistant for Indian Stocks")

# Sidebar - Stock Selection
st.sidebar.header("Select an Indian Stock")
selected_stock = st.sidebar.text_input("Enter NSE Stock Ticker (e.g., RELIANCE.NS, TCS.NS):", "RELIANCE.NS")

# User-defined target price and stop-loss
st.sidebar.header("Trading Strategy")
target_price = st.sidebar.number_input("Set Target Price:", min_value=0.0, value=0.0, step=0.1)
stop_loss = st.sidebar.number_input("Set Stop-Loss Price:", min_value=0.0, value=0.0, step=0.1)

# Fetch Stock Data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    return hist

# Fetch Alternative Data (News Sentiment Analysis)
def get_news_sentiment(ticker):
    api_url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&apiKey=0ba785010ef34b33b31eb4def71e51b4"
    response = requests.get(api_url)
    news_data = response.json()
    
    sentiment_scores = []
    reasons = []
    if "articles" in news_data:
        for article in news_data["articles"][:10]:
            sentiment = TextBlob(article["title"]).sentiment.polarity
            sentiment_scores.append(sentiment)
            reasons.append(article["title"])
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    return avg_sentiment, reasons

# Display Stock Data
st.subheader(f"Stock Data for {selected_stock}")
data = get_stock_data(selected_stock)
st.line_chart(data["Close"], use_container_width=True)

# Sentiment Analysis
sentiment_score, sentiment_reasons = get_news_sentiment(selected_stock)
if sentiment_score > 0:
    sentiment = "📈 Positive"
elif sentiment_score < 0:
    sentiment = "📉 Negative"
else:
    sentiment = "⚖️ Neutral"
st.metric(label="Market Sentiment", value=sentiment)

# Display reasons for stock movement
st.subheader("📢 Reasons for Price Movement")
for reason in sentiment_reasons[:5]:
    st.write(f"- {reason}")

# Stock Alerts
st.subheader("🚨 Smart Stock Alerts")
current_price = data["Close"].iloc[-1]
st.write(f"Current Price: ₹{current_price:.2f}")

if target_price > 0 and current_price >= target_price:
    st.success("🎯 Target price reached! Consider selling.")
if stop_loss > 0 and current_price <= stop_loss:
    st.error("⚠️ Stop-loss triggered! Consider exiting the trade.")

# Additional Insights
st.subheader("📊 Alternative Data Insights")
st.write("More alternative data sources can be integrated, such as social media trends, insider trading insights, and earnings reports.")
st.write("Alternative Data Insights from different sources can enhance decision-making, incorporating factors like global economic indicators, trading volume analytics, and institutional investment trends.")

st.write("---")
st.write("💡 **Powered by AI-driven Analytics & Alternative Data Sources for Indian Markets**")
