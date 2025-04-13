import yfinance as yf
import numpy as np
from config import FUNDAMENTALS_WEIGHT

class FinanceData:
    def get_data(self, stock):
        ticker = yf.Ticker(stock)
        info = ticker.info
        
        # Get 5-day momentum
        hist = ticker.history(period='5d')
        momentum = (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] if not hist.empty else 0
        
        return {
            'pe': info.get('trailingPE'),
            'eps': info.get('trailingEps'),
            'market_cap': info.get('marketCap'),
            'momentum': momentum,
            'price': info.get('currentPrice')
        }

    def calculate_score(self, data):
        score = 0
        if data['pe'] and data['pe'] < 25: score += 1
        if data['eps'] and data['eps'] > 0: score += 1
        if data['market_cap'] and data['market_cap'] > 1e10: score += 1
        if data['momentum'] > 0: score += 1
        return (score / 4) * FUNDAMENTALS_WEIGHT  # Normalize to 0-1 then apply weight