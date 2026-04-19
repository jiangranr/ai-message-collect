"""Hacker News 抓取模块"""
from datetime import datetime
from typing import List, Dict, Any

import httpx
from loguru import logger


class HackerNewsFetcher:
    """Hacker News 抓取器"""

    HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        self.client.close()

    def fetch(self, limit: int = 15) -> List[Dict[str, Any]]:
        """获取Top Stories"""
        items = []

        try:
            # 获取Top Stories ID列表
            response = self.client.get(f"{self.HN_API_BASE}/topstories.json")
            response.raise_for_status()
            story_ids = response.json()[:limit]

            # 获取每个故事的详情
            for story_id in story_ids:
                try:
                    story = self._fetch_story(story_id)
                    if story:
                        items.append(story)
                except Exception as e:
                    logger.warning(f"获取 Story {story_id} 失败: {e}")
                    continue

            logger.info(f"从 Hacker News 获取了 {len(items)} 条资讯")

        except Exception as e:
            logger.warning(f"获取 Hacker News 失败: {e}")

        return items

    def _fetch_story(self, story_id: int) -> Dict[str, Any]:
        """获取单个故事详情"""
        response = self.client.get(f"{self.HN_API_BASE}/item/{story_id}.json")
        response.raise_for_status()
        story = response.json()

        if not story:
            return None

        # 过滤非AI相关内容（通过标题关键词）
        ai_keywords = ["AI", "LLM", "GPT", "ML", "machine learning", "deep learning", "neural"]
        title = story.get("title", "").lower()
        has_ai_keyword = any(kw.lower() in title for kw in ai_keywords)

        # 如果没有AI关键词但有URL，检查URL
        if not has_ai_keyword and story.get("url"):
            url = story["url"].lower()
            has_ai_keyword = any(kw.lower() in url for kw in ai_keywords)

        return {
            "source": "hackernews",
            "source_name": "Hacker News",
            "title": story.get("title", "")[:500],
            "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "summary": story.get("text", "")[:1000] if story.get("text") else "",
            "content": story.get("text", ""),
            "author": story.get("by", ""),
            "published_at": datetime.fromtimestamp(story.get("time", 0)),
            "score": story.get("score", 0),
        }
