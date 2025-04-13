from scraper import Scraper
from finance import FinanceData
from analyzer import Analyzer
from config import STOCKS

def analyze(stock):
    print(f"\n{'='*50}")
    print(f"Analyzing {stock}...")
    print(f"{'='*50}")
    
    # Get data
    scraped = Scraper().scrape(stock)
    finance_data = FinanceData().get_data(stock)
    
    # Prepare texts for sentiment analysis
    texts = (
        [p['title'] + ' ' + p['content'] for p in scraped['reddit']] +
        [n['title'] + ' ' + n.get('description', '') for n in scraped['news']] +
        [w['title'] for w in scraped['web']]
    )
    
    # Analyze with our models
    sentiment = Analyzer().analyze_sentiment(texts)
    fundamental = FinanceData().calculate_score(finance_data)
    decision = Analyzer().make_decision(sentiment, fundamental)
    
    print(f"Sentiment Score: {sentiment:.2f}")
    print(f"Fundamental Score: {fundamental:.2f}")
    print(f"Initial Decision: {decision}")
    
    # Get Gemini's analysis
    gemini_analysis = Analyzer().analyze(
        stock, 
        scraped, 
        finance_data,
        sentiment,
        fundamental,
        decision
    )
    
    print("\nGEMINI ANALYSIS:")
    print(f"{'-'*50}")
    print(gemini_analysis)
    print(f"{'-'*50}")

if __name__ == "__main__":
    for stock in STOCKS:
        analyze(stock)