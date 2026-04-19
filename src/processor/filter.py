"""数据处理模块 - 过滤"""
from typing import List, Dict, Any

from loguru import logger

from config import config


class NewsFilter:
    """新闻过滤器"""

    def __init__(self):
        self.keywords_include = [kw.lower() for kw in config.keywords_include]
        self.keywords_exclude = [kw.lower() for kw in config.keywords_exclude]
        self.min_title_length = config.min_title_length

    def filter(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤资讯列表"""
        filtered = []

        for item in items:
            if self.should_include(item):
                # 记录匹配的关键词
                matched_keywords = self._get_matched_keywords(item)
                item["keywords"] = ",".join(matched_keywords)
                filtered.append(item)

        logger.info(f"过滤完成: {len(items)} -> {len(filtered)} 条")
        return filtered

    def should_include(self, item: Dict[str, Any]) -> bool:
        """判断是否应该包含这条资讯"""
        title = item.get("title", "")
        content = item.get("content", "") or ""
        summary = item.get("summary", "") or ""
        combined = f"{title} {content} {summary}".lower()

        # 1. 标题长度检查
        if len(title) < self.min_title_length:
            return False

        # 2. 排除关键词检查
        for keyword in self.keywords_exclude:
            if keyword in combined:
                return False

        # 3. 包含关键词检查 (必须至少包含一个)
        if self.keywords_include:
            for keyword in self.keywords_include:
                if keyword in combined:
                    return True
            return False

        return True

    def _get_matched_keywords(self, item: Dict[str, Any]) -> List[str]:
        """获取匹配的关键词"""
        title = item.get("title", "").lower()
        content = (item.get("content", "") or "").lower()
        summary = (item.get("summary", "") or "").lower()
        combined = f"{title} {content} {summary}"

        matched = []
        for keyword in self.keywords_include:
            if keyword in combined:
                matched.append(keyword)

        return matched[:5]  # 最多返回5个关键词


class Deduplicator:
    """去重器"""

    def __init__(self):
        self.seen_urls = set()

    def deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        deduplicated = []

        for item in items:
            url = item.get("url", "")
            if not url:
                # 没有URL则使用标题
                title = item.get("title", "")
                if title:
                    url = title[:100]  # 使用标题前100字符作为唯一标识

            if url and url not in self.seen_urls:
                self.seen_urls.add(url)
                deduplicated.append(item)

        logger.info(f"去重完成: {len(items)} -> {len(deduplicated)} 条")
        return deduplicated

    def reset(self):
        """重置已见URL集合"""
        self.seen_urls.clear()
