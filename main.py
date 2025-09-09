from fastapi import FastAPI, Depends, HTTPException, Request
from datetime import datetime
from typing import List
import asyncio

from models.article import NewsResponse, Article
from services.aggregator import ArticleAggregator
from utils.rate_limiter import apply_rate_limit
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="AI News Aggregator",
    description="A comprehensive API that aggregates trending AI news from Reddit, Hacker News, and NewsAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global aggregator instance
aggregator = ArticleAggregator()

@app.get("/", summary="Health Check")
async def root():
    """Basic health check endpoint"""
    return {
        "message": "AI News Aggregator API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", summary="Detailed Health Check")
async def health_check():
    """Detailed health check with service status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rate_limiting": True
        },
        "configuration": {
            "max_articles": settings.total_articles,
            "rate_limit": f"{settings.rate_limit_requests} requests per {settings.rate_limit_period} seconds"
        }
    }

@app.get("/ai-news", response_model=NewsResponse, summary="Get Trending AI News")
async def get_ai_news(request: Request, _: bool = Depends(apply_rate_limit)):
    """
    Get the top 20 trending AI news articles aggregated from multiple sources.
    
    This endpoint aggregates AI news from:
    - Reddit (AI-focused subreddits with community discussions)
    - Hacker News (technical discussions and insights)
    - NewsAPI (mainstream tech publications)
    
    Articles are ranked by engagement metrics, recency, and source quality.
    
    **Response includes:**
    - Article title, description, and URL
    - Source information and publication date
    - Community comments and engagement metrics
    - Total count and sources used
    
    **Rate Limiting:** 100 requests per hour per IP
    """
    
    try:
        # Fetch fresh data
        articles = await aggregator.get_trending_ai_news()
        
        if not articles:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service temporarily unavailable",
                    "message": "Unable to fetch articles from any source. Please try again later."
                }
            )
        
        # Create response
        sources_used = aggregator.get_sources_used(articles)
        response = NewsResponse(
            articles=articles,
            total_count=len(articles),
            sources_used=sources_used,
            last_updated=datetime.now()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_ai_news: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing your request."
            }
        )

@app.get("/sources", summary="Get Available Sources")
async def get_sources():
    """Get information about available news sources"""
    return {
        "sources": [
            {
                "name": "reddit",
                "description": "AI-focused subreddits with community discussions",
                "subreddits": settings.ai_subreddits,
                "provides": ["comments", "upvotes", "community_insights"]
            },
            {
                "name": "hackernews",
                "description": "Technical discussions and startup insights",
                "website": "https://news.ycombinator.com",
                "provides": ["comments", "technical_discussions", "startup_news"]
            },
            {
                "name": "newsapi",
                "description": "Mainstream tech publications and news outlets",
                "search_terms": settings.newsapi_search_terms,
                "provides": ["professional_journalism", "industry_coverage"]
            }
        ],
        "total_target_articles": settings.total_articles,
        "distribution": {
            "reddit": 7,
            "hackernews": 7,
            "newsapi": 6
        }
    }


# Add middleware for CORS if needed
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
