import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from textblob import TextBlob
import requests

# App Title
st.set_page_config(page_title="Invest AI - Smart Indian Stock Insights", layout="wide")
st.title("📈 Invest AI: Advanced Alternative Data Analytics for Indian Stocks")

# Sidebar - Stock Selection
st.sidebar.header("Select an Indian Stock")
selected_stock = st.sidebar.text_input("Enter NSE Stock Ticker (e.g., RELIANCE.NS, TCS.NS):", "RELIANCE.NS")

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
    if "articles" in news_data:
        for article in news_data["articles"][:10]:
            sentiment = TextBlob(article["title"]).sentiment.polarity
            sentiment_scores.append(sentiment)
    return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

# Display Stock Data
st.subheader(f"Stock Data for {selected_stock}")
data = get_stock_data(selected_stock)
st.line_chart(data["Close"], use_container_width=True)

# Sentiment Analysis
sentiment_score = get_news_sentiment(selected_stock)
if sentiment_score > 0:
    sentiment = "📈 Positive"
elif sentiment_score < 0:
    sentiment = "📉 Negative"
else:
    sentiment = "⚖️ Neutral"
st.metric(label="Market Sentiment", value=sentiment)

# Stock Alerts
st.subheader("🚨 Smart Stock Alerts")
if data["Close"].iloc[-1] > data["Close"].mean():
    st.success("Stock is performing well! Consider monitoring closely.")
else:
    st.warning("Stock is below average trend. Caution advised!")

# Additional Insights
st.subheader("📊 Alternative Data Insights")
st.write("More alternative data sources can be integrated, such as social media trends, insider trading insights, and earnings reports.")

st.write("---")
st.write("💡 **Powered by AI-driven Analytics & Alternative Data Sources for Indian Markets**")