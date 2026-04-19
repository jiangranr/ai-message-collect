"""Reddit 抓取模块"""
from datetime import datetime
from typing import List, Dict, Any

import praw
from loguru import logger

from config import config


class RedditFetcher:
    """Reddit 抓取器"""

    def __init__(self):
        self.reddit = None
        self._init_client()

    def _init_client(self):
        """初始化Reddit API客户端"""
        client_id = config.reddit_client_id
        client_secret = config.reddit_client_secret

        if not client_id or not client_secret:
            logger.warning("Reddit API 凭证未配置")
            return

        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=config.reddit_user_agent,
            )
            logger.info("Reddit API 客户端初始化成功")
        except Exception as e:
            logger.error(f"Reddit API 客户端初始化失败: {e}")
            self.reddit = None

    def fetch(self, subreddits: List[str], limit: int = 15) -> List[Dict[str, Any]]:
        """获取子版块热门帖子"""
        if not self.reddit:
            logger.warning("Reddit API 未初始化")
            return []

        items = []

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.hot(limit=limit)

                for post in posts:
                    # 过滤NSFW
                    if post.over_18:
                        continue

                    # 提取URL（如果有自链接则用自链接）
                    url = post.url
                    if hasattr(post, "is_self") and post.is_self:
                        url = f"https://reddit.com{post.permalink}"

                    items.append({
                        "source": "reddit",
                        "source_name": f"r/{subreddit_name}",
                        "title": post.title[:500],
                        "url": url,
                        "summary": post.selftext[:1000] if post.selftext else "",
                        "content": post.selftext,
                        "author": str(post.author) if post.author else "",
                        "published_at": datetime.fromtimestamp(post.created_utc),
                        "score": post.score,
                    })

                logger.info(f"从 r/{subreddit_name} 获取了 {len([p for p in subreddit.hot(limit=limit)])} 条帖子")

            except Exception as e:
                logger.warning(f"获取 r/{subreddit_name} 失败: {e}")
                continue

        return items
