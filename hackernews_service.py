import aiohttp
import asyncio
from typing import List
from datetime import datetime
from models.article import Article, Comment
from config.settings import settings

class HackerNewsService:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_ai_news(self, limit: int = 7) -> List[Article]:
        """Fetch AI-related stories from Hacker News"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        articles = []
        
        try:
            # Get top stories
            top_stories = await self._get_top_stories()
            
            # Process stories in batches to find AI-related ones
            for story_id in top_stories[:100]:  # Check first 100 stories
                if len(articles) >= limit:
                    break
                    
                story = await self._get_story(story_id)
                if story and self._is_ai_related(story.get('title', ''), story.get('text', '')):
                    comments = await self._get_story_comments(story_id)
                    
                    article = Article(
                        title=story.get('title', ''),
                        description=story.get('text', story.get('title', ''))[:500],
                        url=story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                        source="hackernews",
                        score=story.get('score', 0),
                        comments=comments,
                        published_at=datetime.fromtimestamp(story.get('time', 0)),
                        source_id=str(story_id)
                    )
                    articles.append(article)
                    
        except Exception as e:
            print(f"Error fetching from Hacker News: {e}")
            
        return articles[:limit]
    
    async def _get_top_stories(self) -> List[int]:
        """Get list of top story IDs from Hacker News"""
        try:
            async with self.session.get(f"{self.base_url}/topstories.json") as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Error fetching top stories: {e}")
        return []
    
    async def _get_story(self, story_id: int) -> dict:
        """Get individual story details"""
        try:
            async with self.session.get(f"{self.base_url}/item/{story_id}.json") as response:
                if response.status == 200:
                    story = await response.json()
                    # Only return if it's a story (not job, poll, etc.)
                    if story and story.get('type') == 'story':
                        return story
        except Exception as e:
            print(f"Error fetching story {story_id}: {e}")
        return None
    
    async def _get_story_comments(self, story_id: int, max_comments: int = 5) -> List[Comment]:
        """Get top comments for a story"""
        comments = []
        
        try:
            story = await self._get_story(story_id)
            if not story or 'kids' not in story:
                return comments
            
            # Get top comment IDs
            comment_ids = story['kids'][:max_comments]
            
            # Fetch comments concurrently
            comment_tasks = [self._get_comment(comment_id) for comment_id in comment_ids]
            comment_results = await asyncio.gather(*comment_tasks, return_exceptions=True)
            
            for comment_data in comment_results:
                if isinstance(comment_data, dict) and comment_data:
                    comment = Comment(
                        author=comment_data.get('by', 'anonymous'),
                        content=comment_data.get('text', '')[:300],  # Truncate long comments
                        score=0,  # HN doesn't expose comment scores in API
                        created_utc=datetime.fromtimestamp(comment_data.get('time', 0))
                    )
                    comments.append(comment)
                    
        except Exception as e:
            print(f"Error fetching comments for story {story_id}: {e}")
            
        return comments
    
    async def _get_comment(self, comment_id: int) -> dict:
        """Get individual comment details"""
        try:
            async with self.session.get(f"{self.base_url}/item/{comment_id}.json") as response:
                if response.status == 200:
                    comment = await response.json()
                    if comment and comment.get('type') == 'comment' and not comment.get('deleted'):
                        return comment
        except Exception as e:
            print(f"Error fetching comment {comment_id}: {e}")
        return None
    
    def _is_ai_related(self, title: str, text: str) -> bool:
        """Check if the story is related to AI"""
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural network', 'chatgpt', 'gpt', 'openai', 'llm', 'large language model',
            'transformer', 'bert', 'nlp', 'computer vision', 'reinforcement learning',
            'generative ai', 'anthropic', 'claude', 'stable diffusion', 'midjourney',
            'pytorch', 'tensorflow', 'hugging face', 'langchain'
        ]
        
        content = (title + " " + (text or "")).lower()
        return any(keyword in content for keyword in ai_keywords)
