from transformers import pipeline
import google.generativeai as genai
from config import GEMINI_API_KEY, SENTIMENT_WEIGHT, FUNDAMENTALS_WEIGHT, BUY_THRESHOLD, SELL_THRESHOLD

class StockAnalyzer:
    def __init__(self):
        # Initialize FinBERT
        try:
            self.finbert = pipeline("text-classification", model="yiyanghkust/finbert-tone")
        except Exception as e:
            print(f"Error loading FinBERT: {e}")
            self.finbert = None
        
        # Initialize Gemini (if API key available)
        self.gemini = None
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
    
    def analyze_sentiment(self, texts):
        """Analyze sentiment using FinBERT"""
        if not self.finbert or not texts:
            return 0
        
        scores = []
        for text in texts:
            try:
                result = self.finbert(text[:512])[0]  # Limit to first 512 chars
                score = result['score'] if result['label'] == 'positive' else -result['score']
                scores.append(score)
            except Exception as e:
                print(f"Error analyzing text: {e}")
                continue
        
        avg_score = sum(scores)/len(scores) if scores else 0
        return max(0, avg_score) * SENTIMENT_WEIGHT  # Only use positive sentiment
    
    def make_decision(self, sentiment, fundamental):
        """Make initial decision based on scores"""
        total = sentiment + fundamental
        if total >= BUY_THRESHOLD: return "BUY"
        elif total <= SELL_THRESHOLD: return "SELL"
        return "HOLD"
    
    def enhanced_analysis(self, stock, scraped_data, finance_data, sentiment_score=None, fundamental_score=None):
        """
        Perform comprehensive analysis using both FinBERT and Gemini (if available)
        
        Args:
            stock: Stock ticker symbol
            scraped_data: Dictionary containing 'reddit', 'news', 'web' keys
            finance_data: Dictionary of financial metrics
            sentiment_score: Optional pre-calculated score
            fundamental_score: Optional pre-calculated score
            
        Returns:
            Dictionary containing:
            - basic_decision: Simple BUY/SELL/HOLD
            - gemini_analysis: Gemini's detailed analysis (if available)
            - scores: Calculated scores
        """
        # Calculate scores if not provided
        if sentiment_score is None:
            texts = self._prepare_texts_for_analysis(scraped_data)
            sentiment_score = self.analyze_sentiment(texts)
        
        if fundamental_score is None:
            fundamental_score = self._calculate_fundamental_score(finance_data)
        
        basic_decision = self.make_decision(sentiment_score, fundamental_score)
        
        # Get Gemini analysis if available
        gemini_analysis = None
        if self.gemini:
            gemini_analysis = self._get_gemini_analysis(
                stock, scraped_data, finance_data,
                sentiment_score, fundamental_score, basic_decision
            )
        
        return {
            'basic_decision': basic_decision,
            'gemini_analysis': gemini_analysis,
            'scores': {
                'sentiment': sentiment_score,
                'fundamental': fundamental_score,
                'total': sentiment_score + fundamental_score
            }
        }
    
    def _prepare_texts_for_analysis(self, scraped_data):
        """Combine all text sources for sentiment analysis"""
        texts = []
        for source in ['reddit', 'news', 'web']:
            for item in scraped_data.get(source, []):
                if 'title' in item:
                    texts.append(item['title'])
                if 'content' in item and item['content']:
                    texts.append(item['content'])
                if 'body' in item:  # For Reddit comments
                    texts.append(item['body'])
        return texts
    
    def _calculate_fundamental_score(self, finance_data):
        """Calculate fundamental score from financial data"""
        score = 0
        if finance_data.get('pe') and finance_data['pe'] < 25: score += 1
        if finance_data.get('eps') and finance_data['eps'] > 0: score += 1
        if finance_data.get('market_cap') and finance_data['market_cap'] > 1e10: score += 1
        if finance_data.get('momentum', 0) > 0: score += 1
        return (score / 4) * FUNDAMENTALS_WEIGHT
    
    def _get_gemini_analysis(self, stock, scraped_data, finance_data, sentiment_score, fundamental_score, decision):
        """Generate enhanced analysis using Gemini"""
        try:
            # Prepare context data
            context = {
                'stock': stock,
                'reddit_count': len(scraped_data.get('reddit', [])),
                'news_count': len(scraped_data.get('news', [])),
                'web_count': len(scraped_data.get('web', [])),
                'sample_titles': [item.get('title', '') for item in 
                                 scraped_data.get('reddit', [])[:2] + 
                                 scraped_data.get('news', [])[:2] + 
                                 scraped_data.get('web', [])[:2]],
                'finance_data': finance_data,
                'scores': {
                    'sentiment': sentiment_score,
                    'fundamental': fundamental_score,
                    'total': sentiment_score + fundamental_score
                },
                'decision': decision
            }
            
            prompt = self._create_gemini_prompt(context)
            response = self.gemini.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini analysis failed: {str(e)}"
    
    def _create_gemini_prompt(self, context):
        """Create a detailed prompt for Gemini"""
        finance_str = "\n".join([
            f"PE Ratio: {context['finance_data'].get('pe', 'N/A')}",
            f"EPS: {context['finance_data'].get('eps', 'N/A')}",
            f"Market Cap: {context['finance_data'].get('market_cap', 'N/A')}",
            f"5-Day Momentum: {context['finance_data'].get('momentum', 0):.2%}",
            f"Current Price: ${context['finance_data'].get('price', 'N/A')}"
        ])
        
        return f"""
        Provide a professional stock analysis for {context['stock']} with these inputs:
        
        MARKET SENTIMENT:
        - {context['reddit_count']} Reddit discussions
        - {context['news_count']} news articles
        - {context['web_count']} web results
        Sample headlines:
        {chr(10).join(f'- {title}' for title in context['sample_titles'] if title)}
        
        FINANCIAL METRICS:
        {finance_str}
        
        ANALYSIS SCORES:
        - Sentiment: {context['scores']['sentiment']:.2f}/0.7
        - Fundamentals: {context['scores']['fundamental']:.2f}/0.3
        - Total: {context['scores']['total']:.2f}/1.0
        - Initial Decision: {context['decision']}
        
        Your analysis should:
        1. Summarize key positive/negative factors
        2. Assess financial health
        3. Evaluate if the initial decision seems sound
        4. Provide final recommendation (BUY/SELL/HOLD) with confidence level
        5. Highlight important risks
        6. Keep it concise (3-5 paragraphs max)
        """