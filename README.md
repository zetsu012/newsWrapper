# AI News Aggregator API

A comprehensive FastAPI-based service that aggregates trending AI news from multiple sources including Reddit, Hacker News, and NewsAPI. The API returns the top 20 AI articles with titles, descriptions, and community comments, ranked by engagement metrics and recency.

## Features

- **Multi-source aggregation**: Combines AI news from Reddit, Hacker News, and NewsAPI
- **Intelligent ranking**: Articles ranked by engagement metrics, recency, and source quality
- **Community insights**: Includes comments and discussions from Reddit and Hacker News
- **Performance optimized**: Redis caching and rate limiting for optimal performance
- **Real-time data**: Fresh content aggregated from live sources
- **RESTful API**: Clean, documented endpoints with automatic OpenAPI documentation

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reddit API    │    │ Hacker News API │    │    NewsAPI      │
│   (PRAW)        │    │   (Firebase)    │    │  (REST API)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │    Article Aggregator       │
                    │  (Ranking & Deduplication)  │
                    └─────────────┬───────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │     FastAPI Service        │
                    │   (Rate Limiting & Cache)   │
                    └─────────────┬───────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │      JSON Response         │
                    │    (20 Trending Articles)   │
                    └─────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- Redis (optional, for caching)
- API credentials for Reddit and NewsAPI

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RedditNewsWrapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

4. **Get API credentials**

   **Reddit API:**
   - Go to https://www.reddit.com/prefs/apps
   - Create a new application (script type)
   - Copy client ID and secret

   **NewsAPI:**
   - Sign up at https://newsapi.org/
   - Get your free API key

5. **Run the application**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### GET /ai-news

Returns the top 20 trending AI news articles.

**Response:**
```json
{
  "articles": [
    {
      "title": "OpenAI Announces GPT-5 with Revolutionary Capabilities",
      "description": "OpenAI has unveiled GPT-5, featuring...",
      "url": "https://example.com/article",
      "source": "reddit",
      "score": 245,
      "comments": [
        {
          "author": "tech_enthusiast",
          "content": "This is incredible progress...",
          "score": 42,
          "created_utc": "2024-01-15T10:30:00Z"
        }
      ],
      "published_at": "2024-01-15T09:00:00Z",
      "source_id": "abc123"
    }
  ],
  "total_count": 20,
  "sources_used": ["reddit", "hackernews", "newsapi"],
  "last_updated": "2024-01-15T10:35:00Z"
}
```

### GET /sources

Returns information about available news sources.

### GET /health

Health check endpoint with service status.

### POST /cache/clear

Clears the cache (admin function).

## Configuration

Configure the application using environment variables in `.env`:

```env
# Required
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
NEWSAPI_KEY=your_api_key

# Optional
REDIS_HOST=localhost
CACHE_TTL=300
RATE_LIMIT_REQUESTS=100
```

## Data Sources

### Reddit
- **Subreddits**: artificial, MachineLearning, deeplearning, singularity, OpenAI, ChatGPT
- **Provides**: Community discussions, upvotes, user comments
- **Articles**: 7 per request

### Hacker News
- **Source**: Top stories from news.ycombinator.com
- **Provides**: Technical discussions, startup insights, expert commentary
- **Articles**: 7 per request

### NewsAPI
- **Sources**: TechCrunch, The Verge, Wired, MIT Technology Review, etc.
- **Provides**: Professional journalism, industry coverage
- **Articles**: 6 per request

## Ranking Algorithm

Articles are ranked using a composite score based on:

1. **Engagement Score** (40%):
   - Comment count and quality
   - Upvotes/scores from source platforms
   - User interaction metrics

2. **Recency Score** (35%):
   - Time since publication
   - Higher scores for newer content
   - Logarithmic decay over time

3. **Source Quality Score** (25%):
   - Platform credibility rating
   - Historical engagement patterns
   - Content quality indicators

## Performance Features

### Caching
- Redis-based response caching
- 5-minute TTL for optimal freshness
- Automatic cache invalidation

### Rate Limiting
- 100 requests per hour per IP
- Graceful degradation under load
- Custom rate limit headers

### Error Handling
- Graceful service degradation
- Detailed error responses
- Automatic retry logic

## Development

### Project Structure
```
├── main.py                 # FastAPI application
├── models/
│   └── article.py         # Data models
├── services/
│   ├── reddit_service.py  # Reddit integration
│   ├── hackernews_service.py  # Hacker News integration
│   ├── newsapi_service.py # NewsAPI integration
│   └── aggregator.py      # Article aggregation
├── utils/
│   ├── cache.py          # Caching utilities
│   └── rate_limiter.py   # Rate limiting
├── config/
│   └── settings.py       # Configuration management
└── tests/                # Test suite
```

### Running Tests
```bash
pytest tests/
```

### API Documentation

Visit these URLs when the server is running:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t ai-news-aggregator .

# Run container
docker run -p 8000:8000 --env-file .env ai-news-aggregator
```

### Production Considerations
- Use environment-specific configurations
- Set up proper logging and monitoring
- Configure CORS for your frontend domain
- Use a production ASGI server like Gunicorn
- Set up Redis clustering for high availability

## Monitoring

The API provides several monitoring endpoints:

- `/health` - Service health status
- Built-in metrics for response times
- Rate limiting statistics
- Cache hit/miss ratios

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review configuration in `.env.example`
- Verify API credentials are correctly set
