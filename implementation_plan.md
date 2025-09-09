# Implementation Plan

[Overview]
Build a FastAPI-based Python service that aggregates AI news from multiple sources and returns 20 trending articles with titles, descriptions, and comments.

This implementation creates a comprehensive AI news aggregation API that pulls content from Reddit (AI-focused subreddits), Hacker News (technical discussions), and NewsAPI (mainstream tech publications). The system will provide real-time access to the latest AI trends, research discussions, and industry news with rich metadata including user comments and engagement metrics. The API will serve as a one-stop source for staying current with AI developments across different communities and publication types.

[Types]
Define data models and response structures for consistent API responses.

```python
# Pydantic models for API responses
class Comment(BaseModel):
    author: str
    content: str
    score: int
    created_utc: datetime

class Article(BaseModel):
    title: str
    description: str
    url: str
    source: str  # "reddit", "hackernews", "newsapi"
    score: int
    comments: List[Comment]
    published_at: datetime
    source_id: str

class NewsResponse(BaseModel):
    articles: List[Article]
    total_count: int
    sources_used: List[str]
    last_updated: datetime
```

[Files]
Create new project files for a complete FastAPI application.

**New files to be created:**
- `main.py` - FastAPI application entry point and main router
- `models/article.py` - Pydantic models for API responses
- `services/reddit_service.py` - Reddit data fetching using PRAW
- `services/hackernews_service.py` - Hacker News API integration
- `services/newsapi_service.py` - NewsAPI integration
- `services/aggregator.py` - Data aggregation and ranking logic
- `config/settings.py` - Configuration management
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `.env.example` - Environment variables template
- `utils/cache.py` - Caching utilities
- `utils/rate_limiter.py` - Rate limiting implementation

[Functions]
Implement core functionality for data fetching, processing, and API responses.

**New functions:**
- `fetch_reddit_posts()` in `reddit_service.py` - Fetch AI posts from specified subreddits
- `fetch_reddit_comments()` in `reddit_service.py` - Extract comments from Reddit posts
- `fetch_hackernews_stories()` in `hackernews_service.py` - Get trending AI stories from HN
- `fetch_hackernews_comments()` in `hackernews_service.py` - Fetch HN comment threads
- `fetch_news_articles()` in `newsapi_service.py` - Get AI news from NewsAPI
- `aggregate_articles()` in `aggregator.py` - Combine and rank articles from all sources
- `rank_by_engagement()` in `aggregator.py` - Score articles by comments, upvotes, recency
- `get_ai_news()` in `main.py` - Main API endpoint handler
- `cache_response()` in `cache.py` - Cache API responses for performance
- `apply_rate_limit()` in `rate_limiter.py` - Rate limiting middleware

[Classes]
Define service classes for clean separation of concerns.

**New classes:**
- `RedditService` in `reddit_service.py` - Handles all Reddit API interactions, manages PRAW client
- `HackerNewsService` in `hackernews_service.py` - Manages Hacker News API calls and data parsing
- `NewsAPIService` in `newsapi_service.py` - Handles NewsAPI integration and article fetching
- `ArticleAggregator` in `aggregator.py` - Combines articles from all sources, handles ranking logic
- `CacheManager` in `cache.py` - Manages response caching with TTL
- `Settings` in `settings.py` - Configuration management using Pydantic BaseSettings

[Dependencies]
Install required packages for API development and external service integration.

```
fastapi==0.104.1
uvicorn==0.24.0
praw==7.7.1
aiohttp==3.9.1
python-dotenv==1.0.0
pydantic==2.5.0
redis==5.0.1
requests==2.31.0
python-dateutil==2.8.2
```

**Integration requirements:**
- Reddit API credentials (client_id, client_secret, user_agent)
- NewsAPI key for mainstream news access
- Redis server for caching (optional but recommended)

[Testing]
Implement comprehensive testing for reliability and performance validation.

**Test files to create:**
- `tests/test_reddit_service.py` - Unit tests for Reddit integration
- `tests/test_hackernews_service.py` - Unit tests for Hacker News service
- `tests/test_newsapi_service.py` - Unit tests for NewsAPI service
- `tests/test_aggregator.py` - Tests for article ranking and aggregation
- `tests/test_api.py` - Integration tests for API endpoints

**Testing approach:**
- Mock external API calls for unit tests
- Test rate limiting and caching functionality
- Validate response format and data quality
- Performance testing for 20-article response time

[Implementation Order]
Follow a logical sequence to build and test incrementally.

1. **Project Setup** - Create directory structure, requirements.txt, basic FastAPI app
2. **Configuration** - Implement settings management and environment variables
3. **Data Models** - Define Pydantic models for API responses
4. **Reddit Service** - Implement Reddit data fetching with PRAW
5. **Hacker News Service** - Build Hacker News API integration
6. **NewsAPI Service** - Add mainstream news source integration
7. **Article Aggregator** - Create ranking and aggregation logic
8. **Caching Layer** - Implement response caching for performance
9. **Main API Endpoint** - Wire everything together in FastAPI route
10. **Error Handling** - Add comprehensive error handling and validation
11. **Testing** - Create and run test suite
12. **Documentation** - Complete README and API documentation
