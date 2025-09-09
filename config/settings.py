from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Reddit API Configuration
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str = "AI News Aggregator v1.0"
    
    # NewsAPI Configuration
    newsapi_key: str
    
    # Redis Configuration (optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Cache Configuration
    cache_ttl: int = 300  # 5 minutes
    enable_cache: bool = True
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
