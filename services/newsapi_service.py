import aiohttp
from typing import List
from datetime import datetime
from models.article import Article, Comment
from config.settings import settings

class NewsAPIService:
    def __init__(self):
        self.base_url = "https://newsapi.org/v2"
        self.api_key = settings.newsapi_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_ai_news(self, limit: int = 6) -> List[Article]:
        """Fetch AI-related news from NewsAPI"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        articles = []
        
        try:
            # Search for AI-related articles
            for search_term in settings.newsapi_search_terms:
                if len(articles) >= limit:
                    break
                    
                news_articles = await self._search_articles(search_term, limit)
                articles.extend(news_articles)
                
                if len(articles) >= limit:
                    break
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    unique_articles.append(article)
                    
            return unique_articles[:limit]
            
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    async def _search_articles(self, query: str, limit: int) -> List[Article]:
        """Search for articles using NewsAPI"""
        articles = []
        
        try:
            params = {
                'q': query,
                'sortBy': 'popularity',
                'language': 'en',
                'pageSize': min(limit, 20),  # NewsAPI max is 100, but we want recent articles
                'apiKey': self.api_key
            }
            
            async with self.session.get(f"{self.base_url}/everything", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for article_data in data.get('articles', []):
                        if len(articles) >= limit:
                            break
                            
                        # Skip articles without proper content
                        if not article_data.get('title') or article_data.get('title') == '[Removed]':
                            continue
                            
                        article = Article(
                            title=article_data.get('title', ''),
                            description=article_data.get('description', article_data.get('title', ''))[:500],
                            url=article_data.get('url', ''),
                            source="newsapi",
                            score=self._calculate_popularity_score(article_data),
                            comments=[],  # NewsAPI doesn't provide comments
                            published_at=self._parse_datetime(article_data.get('publishedAt')),
                            source_id=article_data.get('url', '')  # Use URL as ID for NewsAPI
                        )
                        articles.append(article)
                        
                elif response.status == 429:
                    print("NewsAPI rate limit exceeded")
                    return articles
                else:
                    print(f"NewsAPI error: {response.status}")
                    return articles
                    
        except Exception as e:
            print(f"Error searching NewsAPI for '{query}': {e}")
            
        return articles
    
    def _calculate_popularity_score(self, article_data: dict) -> int:
        """Calculate a popularity score for NewsAPI articles"""
        # Since NewsAPI doesn't provide engagement metrics,
        # we'll create a simple scoring system based on source and recency
        
        source = article_data.get('source', {}).get('name', '').lower()
        published_at = self._parse_datetime(article_data.get('publishedAt'))
        
        # Base score
        score = 50
        
        # Boost score for reputable tech sources
        tech_sources = [
            'techcrunch', 'ars technica', 'the verge', 'wired', 'venturebeat',
            'ieee spectrum', 'mit technology review', 'ai news', 'artificial intelligence news'
        ]
        
        if any(tech_source in source for tech_source in tech_sources):
            score += 30
            
        # Boost for recency (articles from last 24 hours get bonus points)
        if published_at:
            # Make datetime.now() timezone-aware to match published_at
            current_time = datetime.now(published_at.tzinfo) if published_at.tzinfo else datetime.now()
            hours_ago = (current_time - published_at).total_seconds() / 3600
            if hours_ago < 24:
                score += int(24 - hours_ago)
                
        return score
    
    def _parse_datetime(self, date_string: str) -> datetime:
        """Parse NewsAPI datetime string"""
        try:
            if date_string:
                # NewsAPI uses ISO 8601 format
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except Exception as e:
            print(f"Error parsing datetime '{date_string}': {e}")
            
        return datetime.now()
