import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MyStockAnalyzer/1.0")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SENTIMENT_WEIGHT = 0.7
FUNDAMENTALS_WEIGHT = 0.3

BUY_THRESHOLD = 1.5
SELL_THRESHOLD = 0.5

STOCKS = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"]