from pydantic import BaseModel
from typing import List
from datetime import datetime

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
