"""数据抓取模块"""
from typing import List, Dict, Any

from loguru import logger

from config import config
from .twitter import TwitterFetcher
from .reddit import RedditFetcher
from .hackernews import HackerNewsFetcher
from .rss import RSSFetcher, GenericFetcher
from .financial import FinancialAIFetcher
from .blog_extractor import BlogExtractor


class Fetcher:
    """统一抓取入口"""

    def __init__(self):
        self.twitter = TwitterFetcher() if config.twitter_enabled else None
        self.reddit = RedditFetcher() if config.reddit_enabled else None
        self.hackernews = HackerNewsFetcher() if config.hacker_news_enabled else None
        self.rss = RSSFetcher()
        self.generic = GenericFetcher()
        self.financial = FinancialAIFetcher() if config.financial_ai_enabled else None
        self.blog_extractor = BlogExtractor() if config.blog_enabled else None

    def fetch_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """抓取所有数据源"""
        results = {
            "ai_news": [],       # 通用AI资讯
            "financial_news": [], # 金融AI资讯
            "blog_recommendations": [], # 技术博客推荐
        }

        # 1. 抓取通用AI资讯
        logger.info("开始抓取通用AI资讯...")

        # Twitter
        if self.twitter:
            try:
                tweets = self.twitter.fetch(hours=24)
                results["ai_news"].extend(tweets)
                logger.info(f"Twitter: 获取 {len(tweets)} 条")
            except Exception as e:
                logger.warning(f"Twitter 抓取失败: {e}")

        # Reddit
        if self.reddit:
            try:
                posts = self.reddit.fetch(
                    config.reddit_subreddits,
                    limit=config.reddit_config.get("limit", 15)
                )
                results["ai_news"].extend(posts)
                logger.info(f"Reddit: 获取 {len(posts)} 条")
            except Exception as e:
                logger.warning(f"Reddit 抓取失败: {e}")

        # Hacker News
        if self.hackernews:
            try:
                hn_items = self.hackernews.fetch(limit=15)
                results["ai_news"].extend(hn_items)
                logger.info(f"Hacker News: 获取 {len(hn_items)} 条")
            except Exception as e:
                logger.warning(f"Hacker News 抓取失败: {e}")

        # TechCrunch RSS
        if config.techcrunch_enabled:
            try:
                tc_feeds = [
                    {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"}
                ]
                tc_items = self.rss.fetch_multiple(tc_feeds)
                results["ai_news"].extend(tc_items)
                logger.info(f"TechCrunch: 获取 {len(tc_items)} 条")
            except Exception as e:
                logger.warning(f"TechCrunch 抓取失败: {e}")

        # AI新闻源（The Verge, Wired, MIT Tech Review等）
        if config.ai_news_sources_enabled:
            try:
                ai_news_feeds = []
                for source in config.ai_news_sources_config.get("sources", []):
                    source_type = source.get("type", "web")
                    if source_type == "rss" and source.get("url"):
                        ai_news_feeds.append(source)
                if ai_news_feeds:
                    ai_news_items = self.rss.fetch_multiple(ai_news_feeds)
                    results["ai_news"].extend(ai_news_items)
                    logger.info(f"AI新闻源: 获取 {len(ai_news_items)} 条")
            except Exception as e:
                logger.warning(f"AI新闻源 抓取失败: {e}")

        # AI公司官方博客
        if config.company_blogs_enabled:
            try:
                blog_feeds = []
                for blog in config.company_blogs_config.get("blogs", []):
                    if blog.get("rss"):
                        blog_feeds.append(blog)
                blog_items = self.rss.fetch_multiple(blog_feeds)
                results["ai_news"].extend(blog_items)
                logger.info(f"AI公司博客: 获取 {len(blog_items)} 条")
            except Exception as e:
                logger.warning(f"AI公司博客 抓取失败: {e}")

        # 中文AI媒体
        if config.chinese_media_enabled:
            try:
                chinese_feeds = []
                for source in config.chinese_media_config.get("sources", []):
                    chinese_feeds.append(source)
                chinese_items = self.rss.fetch_multiple(chinese_feeds)
                results["ai_news"].extend(chinese_items)
                logger.info(f"中文AI媒体: 获取 {len(chinese_items)} 条")
            except Exception as e:
                logger.warning(f"中文AI媒体 抓取失败: {e}")

        # 2. 抓取金融AI资讯
        logger.info("开始抓取金融AI资讯...")

        if self.financial:
            try:
                financial_items = self.financial.fetch_all(
                    config.financial_ai_config.get("sources", [])
                )
                results["financial_news"].extend(financial_items)
                logger.info(f"金融AI资讯: 获取 {len(financial_items)} 条")
            except Exception as e:
                logger.warning(f"金融AI资讯 抓取失败: {e}")

        # 3. 提取技术博客推荐
        logger.info("开始提取技术博客推荐...")

        if self.blog_extractor and self.twitter:
            try:
                # 先获取推文
                tweets_with_urls = self.twitter.fetch_with_urls(hours=24)
                # 从推文中提取博客
                blogs = self.blog_extractor.extract_from_tweets(tweets_with_urls)
                results["blog_recommendations"] = blogs
                logger.info(f"技术博客推荐: 获取 {len(blogs)} 篇")
            except Exception as e:
                logger.warning(f"技术博客提取失败: {e}")

        logger.info(f"抓取完成: AI资讯 {len(results['ai_news'])} 条, 金融AI {len(results['financial_news'])} 条, 博客 {len(results['blog_recommendations'])} 篇")

        return results


__all__ = ["Fetcher", "TwitterFetcher", "RedditFetcher", "HackerNewsFetcher", "RSSFetcher", "FinancialAIFetcher", "BlogExtractor"]
