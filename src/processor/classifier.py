"""数据处理模块 - 分类"""
from typing import List, Dict, Any

from loguru import logger

from config import config
from processor.filter import NewsFilter, Deduplicator


class NewsClassifier:
    """新闻分类器"""

    # AI新闻分类
    AI_CATEGORIES = {
        "产品发布": ["release", "announce", "launch", "发布", "新品", "new", "introducing", "unveil", "debut"],
        "技术研究": ["paper", "research", "arxiv", "论文", "study", "framework", "novel", "discover"],
        "融资动态": ["funding", "Series", "round", "融资", "投资", "估值", "invest", "raise", "valuation", "seed", "venture"],
        "开源项目": ["open source", "github", "开源", "library", "repository", "released", "framework", "tool"],
    }

    # 金融AI分类
    FINANCIAL_CATEGORIES = {
        "智能风控": ["风控", "反欺诈", "风险预警", "risk control", "fraud", "risk", "credit risk"],
        "智能客服": ["客服", "智能外呼", "语音客服", "customer service", "chatbot", "virtual assistant"],
        "智能审单": ["审单", "合同", "票据", "invoice", "contract", "document", "智能比对"],
        "智能合规": ["合规", "KYC", "AML", "反洗钱", "compliance", "regulatory", "监管"],
        "智能运营": ["运营", "RPA", "流程", "automation", "流程优化", "数字化", "智能审批"],
        "智能营销": ["营销", "推荐", "画像", "marketing", "recommendation", "个性化", "精准营销"],
    }

    def classify(self, items: List[Dict[str, Any]], is_financial: bool = False) -> List[Dict[str, Any]]:
        """分类资讯列表"""
        categories = self.FINANCIAL_CATEGORIES if is_financial else self.AI_CATEGORIES

        for item in items:
            category = self._classify_item(item, categories)
            item["category"] = category

        # 统计各类别数量
        category_counts = {}
        for item in items:
            cat = item.get("category", "其他")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        logger.info(f"分类完成: {category_counts}")
        return items

    def _classify_item(self, item: Dict[str, Any], categories: Dict[str, List[str]]) -> str:
        """分类单个资讯"""
        title = item.get("title", "").lower()
        content = (item.get("content", "") or "").lower()
        summary = (item.get("summary", "") or "").lower()
        combined = f"{title} {content} {summary}"

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in combined:
                    return category

        return "综合资讯" if not item.get("is_financial") else "金融动态"


class Processor:
    """数据处理入口"""

    def __init__(self):
        self.filter = NewsFilter()
        self.deduplicator = Deduplicator()
        self.classifier = NewsClassifier()

    def process(self, ai_news: List[Dict[str, Any]], financial_news: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """处理所有资讯"""
        results = {
            "ai_news": [],
            "financial_news": [],
        }

        # 1. 处理AI资讯
        if ai_news:
            # 去重
            ai_news = self.deduplicator.deduplicate(ai_news)
            # 过滤
            ai_news = self.filter.filter(ai_news)
            # 分类
            ai_news = self.classifier.classify(ai_news, is_financial=False)
            results["ai_news"] = ai_news

        # 重置去重器
        self.deduplicator.reset()

        # 2. 处理金融AI资讯
        if financial_news:
            # 去重
            financial_news = self.deduplicator.deduplicate(financial_news)
            # 过滤
            financial_news = self.filter.filter(financial_news)
            # 分类
            financial_news = self.classifier.classify(financial_news, is_financial=True)
            results["financial_news"] = financial_news

        logger.info(f"处理完成: AI资讯 {len(results['ai_news'])} 条, 金融AI {len(results['financial_news'])} 条")

        return results


__all__ = ["Processor", "NewsFilter", "Deduplicator", "NewsClassifier"]
