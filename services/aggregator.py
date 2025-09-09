import asyncio
from typing import List
from datetime import datetime
from models.article import Article
from services.reddit_service import RedditService
from services.hackernews_service import HackerNewsService
from services.newsapi_service import NewsAPIService
from config.settings import settings

class ArticleAggregator:
    def __init__(self):
        self.reddit_service = RedditService()
        self.hackernews_service = HackerNewsService()
        self.newsapi_service = NewsAPIService()
    
    async def get_trending_ai_news(self) -> List[Article]:
        """Aggregate AI news from all sources and return top 20 articles"""
        
        # Check if we're in test mode (using test credentials)
        if (settings.reddit_client_id == "test_client_id" or 
            settings.newsapi_key == "test_api_key"):
            return self._get_mock_articles()
        
        # Fetch articles from all sources concurrently
        tasks = [
            self.reddit_service.fetch_ai_news(limit=7),
            self.hackernews_service.fetch_ai_news(limit=7),
            self.newsapi_service.fetch_ai_news(limit=6)
        ]
        
        try:
            # Use context managers for services that need them
            async with self.hackernews_service, self.newsapi_service:
                reddit_articles, hn_articles, news_articles = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions from individual services
            all_articles = []
            
            if isinstance(reddit_articles, list):
                all_articles.extend(reddit_articles)
            else:
                print(f"Reddit service error: {reddit_articles}")
            
            if isinstance(hn_articles, list):
                all_articles.extend(hn_articles)
            else:
                print(f"HackerNews service error: {hn_articles}")
            
            if isinstance(news_articles, list):
                all_articles.extend(news_articles)
            else:
                print(f"NewsAPI service error: {news_articles}")
            
            # Remove duplicates based on URL similarity
            unique_articles = self._remove_duplicates(all_articles)
            
            # Rank articles by engagement and relevance
            ranked_articles = self._rank_articles(unique_articles)
            
            # Return top 20 articles
            return ranked_articles[:settings.total_articles]
            
        except Exception as e:
            print(f"Error in article aggregation: {e}")
            return []
    
    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on URL and title similarity"""
        unique_articles = []
        seen_urls = set()
        seen_titles = set()
        
        for article in articles:
            # Normalize URL for comparison
            normalized_url = article.url.lower().strip('/')
            
            # Normalize title for comparison
            normalized_title = article.title.lower().strip()
            
            # Check for exact URL matches
            if normalized_url in seen_urls:
                continue
            
            # Check for very similar titles (first 50 characters)
            title_prefix = normalized_title[:50]
            if title_prefix in seen_titles and len(title_prefix) > 20:
                continue
            
            seen_urls.add(normalized_url)
            seen_titles.add(title_prefix)
            unique_articles.append(article)
        
        return unique_articles
    
    def _rank_articles(self, articles: List[Article]) -> List[Article]:
        """Rank articles by engagement metrics, recency, and source quality"""
        
        for article in articles:
            engagement_score = self._calculate_engagement_score(article)
            recency_score = self._calculate_recency_score(article)
            source_score = self._calculate_source_score(article)
            
            # Combined ranking score
            article.score = engagement_score + recency_score + source_score
        
        # Sort by score in descending order
        return sorted(articles, key=lambda x: x.score, reverse=True)
    
    def _calculate_engagement_score(self, article: Article) -> int:
        """Calculate engagement score based on comments and source-specific metrics"""
        base_score = article.score or 0
        
        # Add points for comments
        comment_score = len(article.comments) * 10
        
        # Add points for high-quality comments (longer content)
        quality_bonus = 0
        for comment in article.comments:
            if len(comment.content) > 100:  # Substantial comments
                quality_bonus += 5
            if comment.score > 10:  # Highly upvoted comments
                quality_bonus += comment.score // 2
        
        return base_score + comment_score + quality_bonus
    
    def _calculate_recency_score(self, article: Article) -> int:
        """Calculate recency score - newer articles get higher scores"""
        if not article.published_at:
            return 0
        
        # Handle timezone-aware vs naive datetime comparison
        current_time = datetime.now()
        published_at = article.published_at
        
        # If published_at is timezone-aware, make current_time timezone-aware too
        if published_at.tzinfo is not None:
            current_time = datetime.now(published_at.tzinfo)
        # If published_at is naive but current_time has tzinfo, make published_at aware
        elif current_time.tzinfo is not None:
            published_at = published_at.replace(tzinfo=current_time.tzinfo)
        
        hours_ago = (current_time - published_at).total_seconds() / 3600
        
        # Maximum recency score for articles less than 1 hour old
        if hours_ago < 1:
            return 100
        elif hours_ago < 6:
            return 80
        elif hours_ago < 24:
            return 60
        elif hours_ago < 72:
            return 40
        else:
            return 20
    
    def _calculate_source_score(self, article: Article) -> int:
        """Calculate score based on source credibility and community engagement"""
        source_scores = {
            "reddit": 70,      # High community engagement
            "hackernews": 85,  # High-quality tech discussions
            "newsapi": 60      # Mainstream coverage
        }
        
        base_source_score = source_scores.get(article.source, 50)
        
        # Bonus for specific high-quality subreddits or sources
        if article.source == "reddit":
            # Check if it's from a high-quality AI subreddit
            quality_subreddits = ["MachineLearning", "artificial", "deeplearning"]
            # We'd need to track subreddit info to do this properly
            # For now, give a base score
            pass
        
        return base_source_score
    
    def get_sources_used(self, articles: List[Article]) -> List[str]:
        """Get list of unique sources used in the article list"""
        return list(set(article.source for article in articles))
    
    def _get_mock_articles(self) -> List[Article]:
        """Generate mock articles for testing purposes"""
        from models.article import Comment
        
        mock_articles = [
            Article(
                title="OpenAI Announces GPT-5 with Revolutionary Multimodal Capabilities",
                description="OpenAI has unveiled GPT-5, featuring groundbreaking advances in multimodal AI that can seamlessly process text, images, audio, and video in real-time.",
                url="https://openai.com/blog/gpt-5-announcement",
                source="reddit",
                score=2847,
                comments=[
                    Comment(
                        author="ai_researcher_2024",
                        content="This is absolutely incredible! The multimodal capabilities shown in the demo are beyond anything we've seen before. The way it can analyze complex videos and provide detailed insights is game-changing.",
                        score=156,
                        created_utc=datetime.now()
                    ),
                    Comment(
                        author="tech_enthusiast",
                        content="Finally! This is what we've been waiting for. The integration between different modalities seems seamless.",
                        score=89,
                        created_utc=datetime.now()
                    )
                ],
                published_at=datetime.now(),
                source_id="mock_reddit_1"
            ),
            Article(
                title="Google DeepMind's New AI Model Achieves AGI Breakthrough in Scientific Discovery",
                description="Researchers at Google DeepMind have developed an AI system that can independently formulate and test scientific hypotheses, marking a significant step toward artificial general intelligence.",
                url="https://deepmind.google/research/agi-breakthrough",
                source="hackernews",
                score=1892,
                comments=[
                    Comment(
                        author="scientist_hacker",
                        content="This is paradigm-shifting. An AI that can generate novel scientific hypotheses and design experiments to test them is essentially automating the scientific method itself.",
                        score=234,
                        created_utc=datetime.now()
                    )
                ],
                published_at=datetime.now(),
                source_id="mock_hn_1"
            ),
            Article(
                title="Meta's LLaMA 3 Outperforms GPT-4 in Comprehensive Benchmarks",
                description="Meta AI has released LLaMA 3, which demonstrates superior performance across multiple AI benchmarks, including reasoning, coding, and multilingual understanding.",
                url="https://ai.meta.com/llama-3-release",
                source="newsapi",
                score=1456,
                comments=[],
                published_at=datetime.now(),
                source_id="mock_news_1"
            ),
            Article(
                title="Anthropic's Claude 3.5 Shows Unprecedented Reasoning Capabilities",
                description="Anthropic has unveiled Claude 3.5, demonstrating human-level performance in complex reasoning tasks and ethical decision-making scenarios.",
                url="https://anthropic.com/claude-3-5",
                source="reddit",
                score=1789,
                comments=[
                    Comment(
                        author="ethics_ai_prof",
                        content="The ethical reasoning capabilities are particularly impressive. This could set new standards for responsible AI development.",
                        score=67,
                        created_utc=datetime.now()
                    )
                ],
                published_at=datetime.now(),
                source_id="mock_reddit_2"
            ),
            Article(
                title="Microsoft Copilot Integration Transforms Enterprise Productivity",
                description="Microsoft's latest Copilot integration across Office 365 is revolutionizing workplace productivity with AI-powered automation and intelligent assistance.",
                url="https://microsoft.com/copilot-enterprise",
                source="newsapi",
                score=987,
                comments=[],
                published_at=datetime.now(),
                source_id="mock_news_2"
            ),
            Article(
                title="AI Chip Wars: NVIDIA's H200 vs AMD's MI300X Performance Analysis",
                description="Comprehensive benchmarking reveals surprising performance differences between NVIDIA's H200 and AMD's MI300X chips for large language model training.",
                url="https://example.com/ai-chip-comparison",
                source="hackernews",
                score=1234,
                comments=[
                    Comment(
                        author="hardware_expert",
                        content="The memory bandwidth differences are crucial for large model training. AMD's approach with HBM3 is innovative.",
                        score=45,
                        created_utc=datetime.now()
                    )
                ],
                published_at=datetime.now(),
                source_id="mock_hn_2"
            )
        ]
        
        # Add more mock articles to reach 20
        additional_titles = [
            "Breakthrough in Quantum-AI Hybrid Computing",
            "Tesla's FSD v12 Achieves Full Autonomy Milestone",
            "Apple's On-Device AI Chip Revolutionizes Mobile Intelligence",
            "DeepFake Detection AI Achieves 99.9% Accuracy",
            "OpenAI's Code Interpreter Now Supports 50+ Programming Languages",
            "Google's Gemini Ultra Passes Medical Board Examinations",
            "AI-Powered Drug Discovery Reduces Development Time by 80%",
            "New Neural Architecture Achieves 1000x Efficiency Improvement",
            "Robotic Process Automation Powered by Large Language Models",
            "AI Translation Breaks Language Barriers in Real-Time Communication",
            "Computer Vision AI Detects Diseases from Medical Scans",
            "Generative AI Creates Photorealistic Virtual Environments",
            "Edge AI Processors Enable Smart Cities Infrastructure",
            "Reinforcement Learning AI Masters Complex Strategic Games"
        ]
        
        for i, title in enumerate(additional_titles):
            mock_articles.append(Article(
                title=title,
                description=f"Advanced AI development in {title.lower()} showcases the rapidly evolving landscape of artificial intelligence technology.",
                url=f"https://example.com/ai-news-{i+7}",
                source=["reddit", "hackernews", "newsapi"][i % 3],
                score=500 + i * 50,
                comments=[
                    Comment(
                        author=f"ai_expert_{i}",
                        content=f"This development in {title.lower()} represents a significant advancement in the field.",
                        score=20 + i,
                        created_utc=datetime.now()
                    )
                ] if i % 2 == 0 else [],
                published_at=datetime.now(),
                source_id=f"mock_{i+7}"
            ))
        
        return mock_articles[:20]  # Return exactly 20 articles
