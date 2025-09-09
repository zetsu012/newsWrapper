import asyncpraw
from typing import List
from datetime import datetime
from models.article import Article, Comment
from config.settings import settings

class RedditService:
    def __init__(self):
        self.reddit = asyncpraw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent
        )
    
    async def fetch_ai_news(self, limit: int = 7) -> List[Article]:
        """Fetch AI news from specified subreddits"""
        articles = []
        
        for subreddit_name in settings.ai_subreddits:
            try:
                subreddit = await self.reddit.subreddit(subreddit_name)
                
                # Get hot posts from the subreddit
                async for submission in subreddit.hot(limit=limit // len(settings.ai_subreddits) + 1):
                    if len(articles) >= limit:
                        break
                        
                    # Skip stickied posts
                    if submission.stickied:
                        continue
                    
                    # Filter for AI-related content
                    if self._is_ai_related(submission.title, submission.selftext):
                        comments = await self._extract_comments(submission)
                        
                        article = Article(
                            title=submission.title,
                            description=submission.selftext[:500] if submission.selftext else submission.title,
                            url=submission.url,
                            source="reddit",
                            score=submission.score,
                            comments=comments,
                            published_at=datetime.fromtimestamp(submission.created_utc),
                            source_id=submission.id
                        )
                        articles.append(article)
                        
                if len(articles) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        return articles[:limit]
    
    def _is_ai_related(self, title: str, text: str) -> bool:
        """Check if the post is related to AI"""
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural network', 'chatgpt', 'gpt', 'openai', 'llm', 'large language model',
            'transformer', 'bert', 'nlp', 'computer vision', 'reinforcement learning',
            'generative ai', 'anthropic', 'claude', 'stable diffusion', 'midjourney'
        ]
        
        content = (title + " " + text).lower()
        return any(keyword in content for keyword in ai_keywords)
    
    async def _extract_comments(self, submission, max_comments: int = 5) -> List[Comment]:
        """Extract top comments from a Reddit submission"""
        comments = []
        
        try:
            # Ensure comments are loaded
            await submission.comments.replace_more(limit=0)
            
            comment_count = 0
            async for comment in submission.comments:
                if comment_count >= max_comments:
                    break
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    reddit_comment = Comment(
                        author=str(comment.author) if comment.author else "deleted",
                        content=comment.body[:300],  # Truncate long comments
                        score=comment.score,
                        created_utc=datetime.fromtimestamp(comment.created_utc)
                    )
                    comments.append(reddit_comment)
                    comment_count += 1
                    
        except Exception as e:
            print(f"Error extracting comments: {e}")
            
        return comments
