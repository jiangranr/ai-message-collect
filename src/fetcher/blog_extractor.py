"""技术博客提取模块"""
import re
from datetime import date
from typing import List, Dict, Any, Set

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from config import config


class BlogExtractor:
    """技术博客提取器 - 从推文URL中提取博客文章"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)
        self.exclude_domains = config.blog_exclude_domains

    def __del__(self):
        self.client.close()

    def extract_from_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从推文中提取博客链接"""
        # 收集所有URL
        all_urls = []
        for tweet in tweets:
            urls = tweet.get("urls", [])
            author = tweet.get("source_name", "")
            for url in urls:
                all_urls.append({
                    "url": url,
                    "author": author,
                    "tweet_content": tweet.get("title", ""),
                })

        # 过滤和去重
        filtered_urls = self._filter_urls(all_urls)

        # 获取每个URL的标题
        blogs = self._fetch_blog_info(filtered_urls[:config.blog_max_items])

        logger.info(f"从推文提取了 {len(blogs)} 篇博客文章")
        return blogs

    def _filter_urls(self, urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤URL"""
        filtered = []
        seen_domains: Set[str] = set()

        for url_info in urls:
            url = url_info["url"]

            # 跳过短链接
            if "t.co" in url or "bit.ly" in url or "goo.gl" in url:
                continue

            # 提取域名
            domain = self._extract_domain(url)
            if not domain:
                continue

            # 跳过排除的域名
            if any(excluded in domain for excluded in self.exclude_domains):
                continue

            # 跳过图片/视频链接
            if any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".youtube", "video"]):
                continue

            # 保留的域名类型
            allowed_types = [
                "blog", "medium", "substack", "arxiv", "github.com",
                "news", "article", "post", "tech", "dev",
            ]
            # 检查是否可能是博客
            is_blog_like = any(t in domain for t in allowed_types) or "www." not in domain

            # 特殊处理已知博客域名
            blog_domains = [
                "medium.com", "substack.com", "blog.xxx", "dev.to",
                "towardsdatascience.com", "hackernoon.com", "quantamagazine.org",
                "arxiv.org", "github.com", "paperswithcode.com",
            ]
            is_known_blog = any(d in domain for d in blog_domains)

            if is_blog_like or is_known_blog:
                filtered.append(url_info)

        return filtered

    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            match = re.search(r'https?://([^/]+)', url)
            if match:
                return match.group(1).lower()
        except:
            pass
        return ""

    def _fetch_blog_info(self, urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取博客信息"""
        blogs = []

        for url_info in urls:
            url = url_info["url"]
            author = url_info["author"]

            try:
                response = self.client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # 提取标题
                title = ""
                title_elem = soup.select_one("h1, .post-title, .article-title, .entry-title, article h1, title")
                if title_elem:
                    title = title_elem.get_text().strip()
                else:
                    # 从<title>标签提取
                    title_tag = soup.find("title")
                    if title_tag:
                        title = title_tag.get_text().strip()
                        # 清理标题（移除站点名称）
                        title = re.sub(r'\s*[|-–—]\s*.+$', '', title).strip()

                if not title:
                    title = url  # 使用URL作为后备

                # 提取摘要
                summary = ""
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    summary = meta_desc["content"].strip()
                else:
                    og_desc = soup.find("meta", attrs={"property": "og:description"})
                    if og_desc and og_desc.get("content"):
                        summary = og_desc["content"].strip()

                # 限制摘要长度
                summary = summary[:300] if summary else ""

                today = date.today()

                blogs.append({
                    "date": today,
                    "title": title[:500],
                    "url": url,
                    "source_author": author,
                    "summary": summary,
                })

            except Exception as e:
                logger.warning(f"获取博客信息失败 {url}: {e}")
                # 即使获取失败也添加基本记录
                today = date.today()
                blogs.append({
                    "date": today,
                    "title": url[:500],
                    "url": url,
                    "source_author": author,
                    "summary": "",
                })
                continue

        return blogs
