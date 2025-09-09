from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Reddit API Configuration
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "AI News Aggregator v1.0"
    
    # NewsAPI Configuration
    newsapi_key: Optional[str] = None
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # 1 hour
    
    # API Configuration
    max_articles_per_source: int = 10
    total_articles: int = 20
    
    # Subreddits to monitor for AI news
    ai_subreddits: list = [
        "artificial",
        "MachineLearning", 
        "deeplearning",
        "singularity",
        "OpenAI",
        "ChatGPT",
        "singularity"
    ]
    
    # NewsAPI search terms
    newsapi_search_terms: list = [
        "artificial intelligence",
        "machine learning", 
        "AI",
        "neural networks",
        "deep learning",
        "OpenAI",
        "ChatGPT"
    ]
    
    # Redis Configuration (optional for caching)
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    redis_db: Optional[int] = None
    redis_password: Optional[str] = None
    
    # Cache Configuration
    cache_ttl: Optional[int] = None
    enable_cache: Optional[bool] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields to be ignored


# Global settings instance
settings = Settings()
