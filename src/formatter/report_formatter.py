"""格式化模块 - 报告生成"""
from datetime import date, datetime
from typing import List, Dict, Any

from loguru import logger


class ReportFormatter:
    """报告格式化器"""

    def format(self,
               ai_news: List[Dict[str, Any]],
               financial_news: List[Dict[str, Any]],
               blog_recommendations: List[Dict[str, Any]],
               business_ideas: List[Dict[str, Any]]) -> str:
        """格式化完整报告"""
        report_parts = []

        # 标题
        today = date.today().strftime("%Y年%m月%d日")
        report_parts.append(f"# AI Daily Pulse - 每日AI赋能报告")
        report_parts.append(f"**日期**: {today}")
        report_parts.append("")

        # 统计
        report_parts.append(f"**今日摘要**: AI资讯 {len(ai_news)} 条 | 金融AI {len(financial_news)} 条 | 博客推荐 {len(blog_recommendations)} 篇 | 业务建议 {len(business_ideas)} 条")
        report_parts.append("")
        report_parts.append("---")
        report_parts.append("")

        # 板块一：AI最新动态
        report_parts.append("## 📰 板块一：AI最新动态")
        report_parts.append("")
        if ai_news:
            grouped = self._group_by_category(ai_news)
            for category, items in grouped.items():
                report_parts.append(f"### {category}")
                for item in items[:5]:  # 每类最多5条
                    report_parts.append(self._format_news_item(item))
                report_parts.append("")
        else:
            report_parts.append("*暂无AI资讯*")
            report_parts.append("")
        report_parts.append("---")
        report_parts.append("")

        # 板块二：金融AI应用
        report_parts.append("## 💰 板块二：金融AI应用")
        report_parts.append("")
        if financial_news:
            grouped = self._group_by_category(financial_news)
            for category, items in grouped.items():
                report_parts.append(f"### {category}")
                for item in items[:5]:
                    report_parts.append(self._format_news_item(item))
                report_parts.append("")
        else:
            report_parts.append("*暂无金融AI资讯*")
            report_parts.append("")
        report_parts.append("---")
        report_parts.append("")

        # 板块三：技术博客推荐
        if blog_recommendations:
            report_parts.append("## 🎯 技术博客推荐")
            report_parts.append("")
            for i, blog in enumerate(blog_recommendations[:10], 1):
                title = blog.get("title", "")[:80]
                url = blog.get("url", "")
                author = blog.get("source_author", "")
                summary = blog.get("summary", "")

                report_parts.append(f"**{i}. {title}**")
                if author:
                    report_parts.append(f"   来源：@{author}")
                if summary:
                    report_parts.append(f"   {summary[:100]}")
                report_parts.append(f"   [查看原文]({url})")
                report_parts.append("")
        report_parts.append("---")
        report_parts.append("")

        # 板块四：业务赋能建议
        if business_ideas:
            report_parts.append("## 💡 板块三：业务赋能建议")
            report_parts.append("")
            for idea in business_ideas:
                title = idea.get("title", "")
                description = idea.get("description", "")
                difficulty = idea.get("difficulty", "中")
                benefit = idea.get("expected_benefit", "")

                # 难度标签
                diff_icon = {"低": "🟢", "中": "🟡", "高": "🔴"}.get(difficulty, "⚪")

                report_parts.append(f"### 💡 {title}")
                report_parts.append(f"- **描述**: {description}")
                report_parts.append(f"- **实施难度**: {diff_icon} {difficulty}")
                if benefit:
                    report_parts.append(f"- **预期收益**: {benefit}")
                report_parts.append("")

        # 底部
        report_parts.append("---")
        report_parts.append("")
        report_parts.append("*📨 由 AI Daily Pulse 自动生成*")
        report_parts.append("*每日 8:30 定时推送*")

        return "\n".join(report_parts)

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按分类分组"""
        grouped = {}
        for item in items:
            category = item.get("category", "其他")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(item)
        return grouped

    def _format_news_item(self, item: Dict[str, Any]) -> str:
        """格式化单条资讯"""
        title = item.get("title", "")[:100]
        url = item.get("url", "")
        source = item.get("source_name", "")
        summary = item.get("summary", "")

        lines = []
        lines.append(f"- **{title}**")
        if source:
            lines.append(f"  来源: {source}")
        if summary:
            lines.append(f"  {summary[:150]}")
        if url:
            lines.append(f"  [查看原文]({url})")

        return "\n".join(lines)

    def format_simple(self,
                      ai_news: List[Dict[str, Any]],
                      financial_news: List[Dict[str, Any]],
                      blog_recommendations: List[Dict[str, Any]],
                      business_ideas: List[Dict[str, Any]],
                      translate_llm=None) -> str:
        """简洁版报告（适合微信推送）"""
        parts = []

        # 标题
        today = date.today().strftime("%Y年%m月%d日")
        parts.append(f"# AI Daily Pulse - 每日AI赋能报告")
        parts.append(f"**日期**: {today}")
        parts.append("")
        parts.append("---")
        parts.append("")

        # AI资讯 - 只显示翻译后的中文摘要
        if ai_news:
            parts.append("## 📰 板块一：AI最新动态")
            parts.append("")
            for i, item in enumerate(ai_news[:8], 1):
                title = item.get("title", "")
                summary = item.get("summary", "")[:300]
                url = item.get("url", "")
                source = item.get("source_name", "")

                # 只显示翻译后的中文摘要
                chinese_summary = ""
                if translate_llm and summary:
                    try:
                        chinese_summary = translate_llm.translate(summary)
                    except:
                        pass

                parts.append(f"**{i}. {title}**")
                if source:
                    parts.append(f"📌 来源: {source}")
                if chinese_summary:
                    parts.append(f"{chinese_summary}")
                if url:
                    parts.append(f"🔗 原文: {url}")
                parts.append("")
        else:
            parts.append("## 📰 板块一：AI最新动态")
            parts.append("*暂无AI资讯*")
            parts.append("")

        parts.append("---")
        parts.append("")

        # 金融AI - 只显示翻译后的中文摘要
        if financial_news:
            parts.append("## 💰 板块二：金融AI应用")
            parts.append("")
            for i, item in enumerate(financial_news[:5], 1):
                title = item.get("title", "")
                summary = item.get("summary", "")[:300]
                url = item.get("url", "")
                source = item.get("source_name", "")

                # 只显示翻译后的中文摘要
                chinese_summary = ""
                if translate_llm and summary:
                    try:
                        chinese_summary = translate_llm.translate(summary)
                    except:
                        pass

                parts.append(f"**{i}. {title}**")
                if source:
                    parts.append(f"📌 来源: {source}")
                if chinese_summary:
                    parts.append(f"{chinese_summary}")
                if url:
                    parts.append(f"🔗 原文: {url}")
                parts.append("")
        else:
            parts.append("## 💰 板块二：金融AI应用")
            parts.append("*暂无金融AI资讯*")
            parts.append("")

        parts.append("---")
        parts.append("")

        # 博客推荐 - 只显示翻译后的中文摘要
        if blog_recommendations:
            parts.append("## 🎯 板块三：技术博客推荐")
            parts.append("")
            for i, blog in enumerate(blog_recommendations[:5], 1):
                title = blog.get("title", "")
                summary = blog.get("summary", "")[:300]
                url = blog.get("url", "")
                author = blog.get("source_author", "")

                # 只显示翻译后的中文摘要
                chinese_summary = ""
                if translate_llm and summary:
                    try:
                        chinese_summary = translate_llm.translate(summary)
                    except:
                        pass

                parts.append(f"**{i}. {title}**")
                if author:
                    parts.append(f"📌 作者: @{author}")
                if chinese_summary:
                    parts.append(f"{chinese_summary}")
                if url:
                    parts.append(f"🔗 原文: {url}")
                parts.append("")

        parts.append("---")
        parts.append("")

        # 业务建议
        if business_ideas:
            parts.append("## 💡 板块四：业务赋能建议")
            parts.append("")
            for i, idea in enumerate(business_ideas, 1):
                title = idea.get("title", "")
                problem = idea.get("problem", "")
                solution = idea.get("solution", "")
                desc = idea.get("description", "")
                diff = idea.get("difficulty", "中")
                benefit = idea.get("expected_benefit", "")

                diff_icon = {"低": "🟢", "中": "🟡", "高": "🔴"}.get(diff, "⚪")

                parts.append(f"### 💡 {i}. {title}")
                if problem:
                    parts.append(f"❓ **解决的问题**: {problem}")
                if solution:
                    parts.append(f"💡 **解决方案**: {solution}")
                if desc and not solution:
                    parts.append(f"💡 **描述**: {desc}")
                parts.append(f"📊 **实施难度**: {diff_icon} {diff}")
                if benefit:
                    parts.append(f"🎯 **预期收益**: {benefit}")
                parts.append("")

        parts.append("---")
        parts.append("")
        parts.append("*由 AI Daily Pulse 自动生成*")
        parts.append("*每日 8:30 定时推送*")

        return "\n".join(parts)


__all__ = ["ReportFormatter"]
