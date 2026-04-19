"""金融AI资讯 抓取模块"""
from datetime import datetime
from typing import List, Dict, Any

import feedparser
import httpx
from bs4 import BeautifulSoup
from loguru import logger


class FinancialAIFetcher:
    """金融AI资讯 抓取器"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        self.client.close()

    def fetch_all(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量抓取金融AI资讯"""
        all_items = []

        for source in sources:
            url = source.get("url", "")
            name = source.get("name", "unknown")
            source_type = source.get("type", "rss")

            if not url:
                continue

            try:
                if source_type == "rss":
                    items = self._fetch_rss(url, name)
                else:
                    items = self._fetch_web(url, name)

                # 标记为金融相关
                for item in items:
                    item["is_financial"] = True

                all_items.extend(items)
                logger.info(f"从 {name} 获取了 {len(items)} 条金融AI资讯")

            except Exception as e:
                logger.warning(f"抓取 {name} 失败: {e}")
                continue

        return all_items

    def _fetch_rss(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """抓取RSS源"""
        items = []
        try:
            response = self.client.get(url)
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries[:20]:
                try:
                    title = entry.get("title", "").strip()
                    if not title:
                        continue

                    link = entry.get("link", "")
                    if not link:
                        continue

                    summary = ""
                    if hasattr(entry, "summary"):
                        summary = self._clean_html(entry.summary)
                    elif hasattr(entry, "description"):
                        summary = self._clean_html(entry.description)

                    published_at = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            published_at = datetime(*entry.published_parsed[:6])
                        except:
                            pass

                    items.append({
                        "source": "financial",
                        "source_name": source_name,
                        "title": title[:500],
                        "url": link,
                        "summary": summary[:1000] if summary else "",
                        "content": summary,
                        "author": entry.get("author", ""),
                        "published_at": published_at,
                        "is_financial": True,
                    })
                except Exception as e:
                    continue

        except Exception as e:
            logger.warning(f"抓取 RSS {source_name} 失败: {e}")

        return items

    def _fetch_web(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """抓取网页"""
        items = []
        try:
            response = self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # 查找文章列表 - 多种选择器尝试
            selectors = [
                "article",
                ".post-item",
                ".article-item",
                ".news-item",
                ".content-item",
                ".list-item",
                ".item",
            ]

            articles = []
            for selector in selectors:
                articles = soup.select(selector)
                if articles:
                    break

            for article in articles[:20]:
                try:
                    # 提取标题
                    title_elem = article.select_one("h2, h3, h4, .title, .post-title, .article-title, a")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    if not title or len(title) < 5:
                        continue

                    # 提取链接
                    link_elem = article.select_one("a")
                    if not link_elem:
                        continue
                    link = link_elem.get("href", "")
                    if not link:
                        continue
                    if not link.startswith("http"):
                        from urllib.parse import urljoin
                        link = urljoin(url, link)

                    # 提取摘要
                    summary_elem = article.select_one("p, .summary, .desc, .excerpt, .description")
                    summary = summary_elem.get_text().strip() if summary_elem else ""

                    items.append({
                        "source": "financial",
                        "source_name": source_name,
                        "title": title[:500],
                        "url": link,
                        "summary": summary[:1000],
                        "content": summary,
                        "author": "",
                        "published_at": datetime.now(),
                        "is_financial": True,
                    })
                except Exception as e:
                    continue

        except Exception as e:
            logger.warning(f"抓取网页 {source_name} 失败: {e}")

        return items

    def _clean_html(self, html: str) -> str:
        """清理HTML标签"""
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text().strip()
