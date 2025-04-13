# Stock Sentiment Analysis System

A comprehensive tool for analyzing stocks based on sentiment from news, Reddit, and web searches, combined with fundamental financial data analysis and AI-driven insights.

## Features

- Multi-source data collection (Reddit, News API, DuckDuckGo search)
- Sentiment analysis using FinBERT
- Financial data analysis with yfinance
- AI-driven insights with Google's Gemini model
- Customizable analysis weights and decision thresholds

## Setup

1. Clone the repository:

```bash
git clone https://github.com/megh06/FinMagic.git
cd FinMagic
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:

```
REDDIT_CLIENT_ID="your-reddit-client-id"
REDDIT_CLIENT_SECRET="your-reddit-secret"
REDDIT_USER_AGENT="MyStockAnalyzer/1.0"
NEWSAPI_KEY="your-news-api-key"
GEMINI_API_KEY="your-gemini-api-key"
```

## Usage

Run the main script to analyze the stocks defined in config.py:

```bash
python main.py
```

## Configuration

Modify `config.py` to:

- Change the stocks to analyze
- Adjust sentiment and fundamental analysis weights
- Change decision thresholds

## Required API Keys

- **Reddit API**: Register at https://www.reddit.com/prefs/apps
- **Gemini API** : Get API key from https://ai.google.dev/

## File Structure

- `config.py`: Configuration parameters and settings
- `scraper.py`: Web scraping functionality
- `finance.py`: Financial data analysis
- `analyzer.py`: Sentiment analysis
- `gemini_analyzer.py`: AI-driven analysis with Gemini
- `main.py`: Main execution script
