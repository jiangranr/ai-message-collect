"""Twitter 抓取模块"""
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import tweepy
from loguru import logger

from config import config


class TwitterFetcher:
    """Twitter 抓取器"""

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化Twitter API客户端"""
        bearer_token = config.twitter_bearer_token
        if not bearer_token:
            logger.warning("Twitter Bearer Token 未配置")
            return

        try:
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=config.twitter_api_key,
                consumer_secret=config.twitter_api_secret,
                access_token=config.twitter_access_token,
                access_token_secret=config.twitter_access_token_secret,
                wait_on_rate_limit=True,
            )
            logger.info("Twitter API 客户端初始化成功")
        except Exception as e:
            logger.error(f"Twitter API 客户端初始化失败: {e}")
            self.client = None

    def fetch(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取关注账号的最新推文"""
        if not self.client:
            logger.warning("Twitter API 未初始化")
            return []

        items = []
        accounts = config.twitter_accounts

        for account in accounts:
            try:
                user_tweets = self._fetch_user_tweets(account, hours)
                items.extend(user_tweets)
                logger.info(f"从 @{account} 获取了 {len(user_tweets)} 条推文")
            except Exception as e:
                logger.warning(f"获取 @{account} 推文失败: {e}")
                continue

        return items

    def _fetch_user_tweets(self, username: str, hours: int) -> List[Dict[str, Any]]:
        """获取单个用户的推文"""
        if not self.client:
            return []

        try:
            # 获取用户ID
            user = self.client.get_user(username=username.replace("@", ""))
            if not user.data:
                return []

            user_id = user.data.id

            # 计算时间范围
            start_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"

            # 获取推文
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=20,
                start_time=start_time,
                tweet_fields=["created_at", "public_metrics", "text"],
                expansions=["author_id"],
            )

            if not tweets.data:
                return []

            items = []
            for tweet in tweets.data:
                # 过滤转推和回复
                if tweet.text.startswith("RT ") or " @" in tweet.text[:20]:
                    continue

                # 提取URL
                urls = self._extract_urls(tweet.text)

                items.append({
                    "source": "twitter",
                    "source_name": username,
                    "title": tweet.text[:200],  # 标题取前200字符
                    "url": f"https://twitter.com/{username}/status/{tweet.id}",
                    "content": tweet.text,
                    "author": username,
                    "published_at": tweet.created_at,
                    "urls": urls,  # 包含的URL列表
                })

            return items

        except tweepy.TooManyRequests:
            logger.warning(f"Twitter API 速率限制，等待后重试...")
            return []
        except Exception as e:
            logger.warning(f"获取用户 {username} 推文出错: {e}")
            return []

    def _extract_urls(self, text: str) -> List[str]:
        """从文本中提取URL"""
        url_pattern = re.compile(r'https?://[^\s]+')
        urls = url_pattern.findall(text)
        return [url.rstrip('.,;:)') for url in urls]

    def fetch_with_urls(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取包含URL的推文（用于博客提取）"""
        all_tweets = self.fetch(hours)
        tweets_with_urls = []

        for tweet in all_tweets:
            if tweet.get("urls"):
                tweets_with_urls.append(tweet)

        return tweets_with_urls
