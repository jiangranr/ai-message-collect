"""数据库操作"""
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, NewsItem, BusinessIdea, Feedback, DailyReport, BlogRecommendation


class Database:
    """数据库操作类"""

    def __init__(self, db_path: str):
        # 确保目录存在
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # 创建数据库连接
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.Session = sessionmaker(bind=self.engine)

        # 创建表
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.Session()

    # ========== NewsItem 操作 ==========

    def add_news_item(self, item_data: dict) -> Optional[NewsItem]:
        """添加资讯条目"""
        session = self.get_session()
        try:
            # 检查URL是否已存在
            existing = session.query(NewsItem).filter(NewsItem.url == item_data.get("url")).first()
            if existing:
                return None

            item = NewsItem(**item_data)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_news_items_batch(self, items_data: List[dict]) -> int:
        """批量添加资讯条目"""
        session = self.get_session()
        added_count = 0
        try:
            for item_data in items_data:
                existing = session.query(NewsItem).filter(
                    NewsItem.url == item_data.get("url")
                ).first()
                if not existing:
                    item = NewsItem(**item_data)
                    session.add(item)
                    added_count += 1
            session.commit()
            return added_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_news_items_since(self, since: datetime, is_financial: Optional[bool] = None) -> List[NewsItem]:
        """获取指定时间之后的资讯"""
        session = self.get_session()
        try:
            query = session.query(NewsItem).filter(NewsItem.published_at >= since)
            if is_financial is not None:
                query = query.filter(NewsItem.is_financial == is_financial)
            return query.order_by(NewsItem.published_at.desc()).all()
        finally:
            session.close()

    def get_today_news_items(self, is_financial: Optional[bool] = None) -> List[NewsItem]:
        """获取今日资讯"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_news_items_since(today, is_financial)

    # ========== BusinessIdea 操作 ==========

    def add_business_idea(self, idea_data: dict) -> BusinessIdea:
        """添加业务建议"""
        session = self.get_session()
        try:
            idea = BusinessIdea(**idea_data)
            session.add(idea)
            session.commit()
            session.refresh(idea)
            return idea
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_business_ideas_batch(self, ideas_data: List[dict]) -> int:
        """批量添加业务建议"""
        session = self.get_session()
        added_count = 0
        try:
            for idea_data in ideas_data:
                idea = BusinessIdea(**idea_data)
                session.add(idea)
                added_count += 1
            session.commit()
            return added_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_business_ideas_by_date(self, report_date: date) -> List[BusinessIdea]:
        """获取指定日期的业务建议"""
        session = self.get_session()
        try:
            return session.query(BusinessIdea).filter(
                BusinessIdea.date == report_date
            ).order_by(BusinessIdea.idea_number).all()
        finally:
            session.close()

    def clear_business_ideas_by_date(self, report_date: date) -> int:
        """清除指定日期的业务建议"""
        session = self.get_session()
        try:
            count = session.query(BusinessIdea).filter(
                BusinessIdea.date == report_date
            ).delete()
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ========== Feedback 操作 ==========

    def add_feedback(self, feedback_data: dict) -> Feedback:
        """添加反馈"""
        session = self.get_session()
        try:
            feedback = Feedback(**feedback_data)
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            return feedback
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_feedback_by_idea_id(self, idea_id: int) -> List[Feedback]:
        """获取指定建议的反馈"""
        session = self.get_session()
        try:
            return session.query(Feedback).filter(Feedback.idea_id == idea_id).all()
        finally:
            session.close()

    def get_all_feedback(self) -> List[Feedback]:
        """获取所有反馈"""
        session = self.get_session()
        try:
            return session.query(Feedback).order_by(Feedback.created_at.desc()).all()
        finally:
            session.close()

    # ========== DailyReport 操作 ==========

    def add_daily_report(self, report_data: dict) -> DailyReport:
        """添加每日报告"""
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(DailyReport).filter(
                DailyReport.date == report_data.get("date")
            ).first()
            if existing:
                # 更新
                existing.content = report_data.get("content")
                existing.ai_news_count = report_data.get("ai_news_count", 0)
                existing.financial_news_count = report_data.get("financial_news_count", 0)
                existing.blog_recommendations_count = report_data.get("blog_recommendations_count", 0)
                existing.business_ideas_count = report_data.get("business_ideas_count", 0)
                session.commit()
                session.refresh(existing)
                return existing

            report = DailyReport(**report_data)
            session.add(report)
            session.commit()
            session.refresh(report)
            return report
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_daily_report_by_date(self, report_date: date) -> Optional[DailyReport]:
        """获取指定日期的报告"""
        session = self.get_session()
        try:
            return session.query(DailyReport).filter(DailyReport.date == report_date).first()
        finally:
            session.close()

    # ========== BlogRecommendation 操��� ==========

    def add_blog_recommendation(self, blog_data: dict) -> Optional[BlogRecommendation]:
        """添加博客推荐"""
        session = self.get_session()
        try:
            # 检查URL是否已存在
            existing = session.query(BlogRecommendation).filter(
                BlogRecommendation.url == blog_data.get("url")
            ).first()
            if existing:
                return None

            blog = BlogRecommendation(**blog_data)
            session.add(blog)
            session.commit()
            session.refresh(blog)
            return blog
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_blog_recommendations_batch(self, blogs_data: List[dict]) -> int:
        """批量添加博客推荐"""
        session = self.get_session()
        added_count = 0
        try:
            for blog_data in blogs_data:
                existing = session.query(BlogRecommendation).filter(
                    BlogRecommendation.url == blog_data.get("url")
                ).first()
                if not existing:
                    blog = BlogRecommendation(**blog_data)
                    session.add(blog)
                    added_count += 1
            session.commit()
            return added_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_today_blog_recommendations(self) -> List[BlogRecommendation]:
        """获取今日博客推荐"""
        today = date.today()
        session = self.get_session()
        try:
            return session.query(BlogRecommendation).filter(
                BlogRecommendation.date == today
            ).all()
        finally:
            session.close()

    def clear_blog_recommendations_by_date(self, report_date: date) -> int:
        """清除指定日期的博客推荐"""
        session = self.get_session()
        try:
            count = session.query(BlogRecommendation).filter(
                BlogRecommendation.date == report_date
            ).delete()
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
