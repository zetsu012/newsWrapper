import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Initialize with error handling
app = None
handler = None

try:
    from fastapi import FastAPI, HTTPException, Request, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from mangum import Mangum
    from datetime import datetime
    from typing import List, Optional
    import asyncio
    import traceback

    # Import models and core components with error handling
    from models.article import NewsResponse, Article
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

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global aggregator instance - initialized lazily
    _aggregator = None

    def get_aggregator():
        """Lazy initialization of the aggregator with error handling"""
        global _aggregator
        if _aggregator is None:
            try:
                from services.aggregator import ArticleAggregator
                _aggregator = ArticleAggregator()
            except Exception as e:
                print(f"Failed to initialize aggregator: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                # Return a mock aggregator for fallback
                _aggregator = MockAggregator()
        return _aggregator

    class MockAggregator:
        """Fallback aggregator for when services fail to initialize"""
        
        def __init__(self):
            print("Using mock aggregator due to service initialization failure")
        
        async def get_trending_ai_news(self) -> List[Article]:
            """Return mock articles when real services are unavailable"""
            from models.article import Comment
            
            mock_articles = [
                Article(
                    title="AI Service Temporarily Unavailable - Mock Data",
                    description="The news aggregation service is currently experiencing issues. This is placeholder content.",
                    url="https://example.com/service-unavailable",
                    source="system",
                    score=100,
                    comments=[
                        Comment(
                            author="system",
                            content="Service is temporarily unavailable. Please try again later.",
                            score=0,
                            created_utc=datetime.now()
                        )
                    ],
                    published_at=datetime.now(),
                    source_id="mock_system"
                )
            ]
            return mock_articles
        
        def get_sources_used(self, articles: List[Article]) -> List[str]:
            """Return mock sources"""
            return ["system"]

    @app.get("/", summary="Health Check")
    async def root():
        """Basic health check endpoint"""
        return {
            "message": "AI News Aggregator API is running",
            "version": "1.0.0",
            "docs": "/docs",
            "status": "healthy"
        }

    @app.get("/health", summary="Detailed Health Check")
    async def health_check():
        """Detailed health check with service status"""
        try:
            aggregator = get_aggregator()
            service_status = "healthy" if not isinstance(aggregator, MockAggregator) else "degraded"
            
            return {
                "status": service_status,
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "rate_limiting": True,
                    "aggregator": service_status
                },
                "configuration": {
                    "max_articles": getattr(settings, 'total_articles', 20),
                    "rate_limit": f"{getattr(settings, 'rate_limit_requests', 100)} requests per {getattr(settings, 'rate_limit_period', 3600)} seconds"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
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
            # Get aggregator instance (lazy initialization)
            aggregator = get_aggregator()
            
            # Fetch articles with timeout protection
            try:
                articles = await asyncio.wait_for(
                    aggregator.get_trending_ai_news(), 
                    timeout=25.0  # Vercel has 30s timeout, leave 5s buffer
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "Service timeout",
                        "message": "Request timed out while fetching articles. Please try again."
                    }
                )
            
            if not articles:
                # If aggregator returns no articles, provide helpful error
                if isinstance(aggregator, MockAggregator):
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": "Service temporarily unavailable",
                            "message": "News aggregation services are currently unavailable. Please try again later.",
                            "fallback": "Mock data provided"
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": "No articles available",
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
            print(f"Unexpected error in get_ai_news: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred while processing your request.",
                    "debug": str(e) if os.getenv("DEBUG") else None
                }
            )

    @app.get("/sources", summary="Get Available Sources")
    async def get_sources():
        """Get information about available news sources"""
        try:
            aggregator = get_aggregator()
            service_status = "available" if not isinstance(aggregator, MockAggregator) else "degraded"
            
            return {
                "status": service_status,
                "sources": [
                    {
                        "name": "reddit",
                        "description": "AI-focused subreddits with community discussions",
                        "subreddits": getattr(settings, 'ai_subreddits', []),
                        "provides": ["comments", "upvotes", "community_insights"],
                        "status": service_status
                    },
                    {
                        "name": "hackernews",
                        "description": "Technical discussions and startup insights",
                        "website": "https://news.ycombinator.com",
                        "provides": ["comments", "technical_discussions", "startup_news"],
                        "status": service_status
                    },
                    {
                        "name": "newsapi",
                        "description": "Mainstream tech publications and news outlets",
                        "search_terms": getattr(settings, 'newsapi_search_terms', []),
                        "provides": ["professional_journalism", "industry_coverage"],
                        "status": service_status
                    }
                ],
                "total_target_articles": getattr(settings, 'total_articles', 20),
                "distribution": {
                    "reddit": 7,
                    "hackernews": 7,
                    "newsapi": 6
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "sources": []
            }

    # Create the handler for Vercel with proper error handling
    try:
        handler = Mangum(app, lifespan="off")
    except Exception as e:
        print(f"Failed to create Mangum handler: {e}")
        # Create a minimal handler fallback
        def handler(event, context):
            return {
                "statusCode": 500,
                "body": '{"error": "Handler initialization failed"}'
            }

except Exception as e:
    print(f"Critical import error: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Create minimal fallback app and handler
    from datetime import datetime
    import traceback
    
    class MinimalApp:
        def __call__(self, scope, receive, send):
            pass
    
    app = MinimalApp()
    
    def handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "Service initialization failed", "message": "Please check server logs"}'
        }

# Ensure exports are available
if app is None:
    class MinimalApp:
        def __call__(self, scope, receive, send):
            pass
    app = MinimalApp()

if handler is None:
    def handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "Handler not initialized"}'
        }

# Export for Vercel
__all__ = ["app", "handler"]
