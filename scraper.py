import requests
from bs4 import BeautifulSoup
import praw
import json
from datetime import datetime
from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT
)

class Scraper:
    def __init__(self):
        self.reddit = self._setup_reddit()
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0'}

    def _setup_reddit(self):
        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
            return None
        return praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def scrape(self, stock):
        data = {'reddit': [], 'news': [], 'web': []}
        
        # Scrape Reddit
        if self.reddit:
            data['reddit'] = self._scrape_reddit(stock)
        
        # Always scrape web via DuckDuckGo
        data['web'] = self._scrape_web(stock)
        
        return data

    def _scrape_reddit(self, stock):
        results = []
        try:
            for post in self.reddit.subreddit('stocks+investing+wallstreetbets').search(f"${stock}", limit=10):
                results.append({
                    'title': post.title,
                    'content': post.selftext,
                    'score': post.score,
                    'url': post.url
                })
        except Exception as e:
            print(f"Reddit scrape error: {e}")
        return results

    def _scrape_web(self, stock):
        try:
            url = f"https://duckduckgo.com/html/?q={stock}+stock+news"
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            return [{'title': a.text, 'url': a['href']} 
                   for a in soup.select('.result__title a')]
        except:
            return []