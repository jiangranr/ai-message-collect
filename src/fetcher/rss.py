"""RSS 抓取模块"""
from datetime import datetime
from typing import List, Dict, Any, Optional

import feedparser
import httpx
from bs4 import BeautifulSoup
from loguru import logger

from config import config


class RSSFetcher:
    """RSS 抓取器"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        self.client.close()

    def fetch_feed(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """抓取单个RSS源"""
        items = []
        try:
            response = self.client.get(url)
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries[:20]:  # 最多取20条
                try:
                    item = self._parse_entry(entry, source_name)
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.warning(f"解析条目失败: {e}")
                    continue

            logger.info(f"从 {source_name} 获取了 {len(items)} 条资讯")

        except httpx.HTTPError as e:
            logger.warning(f"抓取 {source_name} 失败: {e}")
        except Exception as e:
            logger.warning(f"解析 {source_name} 失败: {e}")

        return items

    def _parse_entry(self, entry: Any, source_name: str) -> Optional[Dict[str, Any]]:
        """解析单个RSS条目"""
        # 获取标题
        title = entry.get("title", "").strip()
        if not title:
            return None

        # 获取链接
        url = entry.get("link", "")
        if not url:
            return None

        # 获取摘要/描述
        summary = ""
        if hasattr(entry, "summary"):
            summary = self._clean_html(entry.summary)
        elif hasattr(entry, "description"):
            summary = self._clean_html(entry.description)

        # 获取发布时间
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except:
                pass
        elif hasattr(entry, "published"):
            try:
                published_at = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            except:
                pass

        return {
            "source": "rss",
            "source_name": source_name,
            "title": title[:500],
            "url": url,
            "summary": summary[:1000] if summary else "",
            "content": summary,
            "author": entry.get("author", ""),
            "published_at": published_at,
        }

    def _clean_html(self, html: str) -> str:
        """清理HTML标签"""
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text().strip()

    def fetch_multiple(self, feeds: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """批量抓取多个RSS源"""
        all_items = []

        for feed in feeds:
            url = feed.get("url", "")
            name = feed.get("name", feed.get("source_name", "unknown"))
            feed_type = feed.get("type", "rss")

            if feed_type == "rss" and url:
                items = self.fetch_feed(url, name)
                all_items.extend(items)

        return all_items


class GenericFetcher:
    """通用网页抓取器（用于非RSS源）"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        self.client.close()

    def fetch_page(self, url: str, source_name: str, selector: str = "article") -> List[Dict[str, Any]]:
        """抓取网页内容"""
        items = []
        try:
            response = self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # 查找文章列表
            articles = soup.select(selector)
            if not articles:
                # 尝试其他常见选择器
                articles = soup.select(".post-item, .article-item, .news-item, .content-item")

            for article in articles[:20]:
                try:
                    item = self._parse_article(article, source_name, url)
                    if item:
                        items.append(item)
                except Exception as e:
                    continue

            logger.info(f"从 {source_name} 页面获取了 {len(items)} 条资讯")

        except Exception as e:
            logger.warning(f"抓取 {source_name} 页面失败: {e}")

        return items

    def _parse_article(self, article: BeautifulSoup, source_name: str, base_url: str) -> Optional[Dict[str, Any]]:
        """解析文章元素"""
        # 提取标题
        title_elem = article.select_one("h2, h3, h4, .title, .post-title, .article-title")
        if not title_elem:
            return None
        title = title_elem.get_text().strip()
        if not title:
            return None

        # 提取链接
        link_elem = article.select_one("a")
        if not link_elem:
            return None
        url = link_elem.get("href", "")
        if url and not url.startswith("http"):
            from urllib.parse import urljoin
            url = urljoin(base_url, url)

        # 提取摘要
        summary_elem = article.select_one("p, .summary, .desc, .excerpt, .description")
        summary = summary_elem.get_text().strip() if summary_elem else ""

        return {
            "source": "web",
            "source_name": source_name,
            "title": title[:500],
            "url": url,
            "summary": summary[:1000],
            "content": summary,
            "author": "",
            "published_at": datetime.now(),
        }
