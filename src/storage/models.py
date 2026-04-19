"""数据模型"""
import json
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class NewsItem(Base):
    """资讯条目"""
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)  # twitter, reddit, huxiu, weidaoke...
    source_name = Column(String(100))  # 来源名称，如 @karpathy
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True)  # 原文链接
    summary = Column(Text)  # 摘要
    content = Column(Text)  # 完整内容
    author = Column(String(100))  # 作者
    published_at = Column(DateTime)  # 发布时间
    category = Column(String(50))  # 分类：产品发布/技术研究/金融应用...
    is_financial = Column(Boolean, default=False)  # 是否金融相关
    keywords = Column(String(200))  # 匹配的关键词
    is_sent = Column(Boolean, default=False)  # 是否已发送
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "source_name": self.source_name,
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "content": self.content,
            "author": self.author,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "category": self.category,
            "is_financial": self.is_financial,
            "keywords": self.keywords,
            "is_sent": self.is_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BusinessIdea(Base):
    """业务建议"""
    __tablename__ = "business_ideas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)  # 日期
    idea_number = Column(Integer, nullable=False)  # 建议序号（1-5）
    title = Column(String(200), nullable=False)  # 建议标题
    description = Column(Text)  # 建议描述
    difficulty = Column(String(10))  # 实施难度：低/中/高
    expected_benefit = Column(String(200))  # 预期收益
    source_items = Column(Text)  # 关联的资讯ID（JSON数组）
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "idea_number": self.idea_number,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "expected_benefit": self.expected_benefit,
            "source_items": json.loads(self.source_items) if self.source_items else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Feedback(Base):
    """用户反馈"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("business_ideas.id"))  # 关联的建议ID
    feedback_type = Column(String(50))  # 有用/没用/太复杂/需要更多细节
    user_comment = Column(Text)  # 用户补充评论
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "idea_id": self.idea_id,
            "feedback_type": self.feedback_type,
            "user_comment": self.user_comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DailyReport(Base):
    """每日报告"""
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True, nullable=False)  # 日期
    content = Column(Text)  # 完整的Markdown内容
    ai_news_count = Column(Integer, default=0)  # AI资讯数量
    financial_news_count = Column(Integer, default=0)  # 金融AI资讯数量
    blog_recommendations_count = Column(Integer, default=0)  # 博客推荐数量
    business_ideas_count = Column(Integer, default=0)  # 业务建议数量
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "content": self.content,
            "ai_news_count": self.ai_news_count,
            "financial_news_count": self.financial_news_count,
            "blog_recommendations_count": self.blog_recommendations_count,
            "business_ideas_count": self.business_ideas_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BlogRecommendation(Base):
    """技术博客推荐"""
    __tablename__ = "blog_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)  # 日期
    title = Column(String(500), nullable=False)  # 文章标题
    url = Column(String(1000), nullable=False)  # 文章链接
    source_author = Column(String(100))  # 来源KOL
    summary = Column(Text)  # 简介
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "title": self.title,
            "url": self.url,
            "source_author": self.source_author,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
