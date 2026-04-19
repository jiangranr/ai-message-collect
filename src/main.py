"""AI Daily Pulse 主程序"""
import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from config import config
from storage import Database
from fetcher import Fetcher
from processor import Processor
from generator import BusinessIdeaGenerator
from formatter import ReportFormatter, Translator
from publisher import Publisher


def setup_logging():
    """配置日志"""
    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=config.log_level,
    )

    # 添加文件输出
    log_file = config.log_file
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )


class AIDailyPulse:
    """AI Daily Pulse 主类"""

    def __init__(self):
        self.db = Database(config.database_path)
        self.fetcher = Fetcher()
        self.processor = Processor()
        self.generator = BusinessIdeaGenerator() if config.generator_enabled else None
        self.formatter = ReportFormatter()
        self.translator = Translator() if config.generator_enabled else None
        self.publisher = Publisher()
        self.today = date.today()

    def run(self):
        """运行主流程"""
        logger.info("=" * 50)
        logger.info("AI Daily Pulse 开始运行")
        logger.info("=" * 50)

        try:
            # 1. 抓取数据
            logger.info("[1/6] 开始抓取数据...")
            raw_data = self.fetcher.fetch_all()
            ai_news = raw_data.get("ai_news", [])
            financial_news = raw_data.get("financial_news", [])
            blog_recommendations = raw_data.get("blog_recommendations", [])
            logger.info(f"抓取完成: AI {len(ai_news)} 条, 金融 {len(financial_news)} 条, 博客 {len(blog_recommendations)} 篇")

            # 2. 处理数据
            logger.info("[2/6] 开始处理数据...")
            processed = self.processor.process(ai_news, financial_news)
            ai_news = processed.get("ai_news", [])
            financial_news = processed.get("financial_news", [])
            logger.info(f"处理完成: AI {len(ai_news)} 条, 金融 {len(financial_news)} 条")

            # 3. 保存到数据库
            logger.info("[3/6] 开始保存数据...")
            self._save_data(ai_news, financial_news, blog_recommendations)
            logger.info("数据保存完成")

            # 4. 生成业务建议
            logger.info("[4/6] 开始生成业务建议...")
            business_ideas = []
            if self.generator and (ai_news or financial_news):
                business_ideas = self.generator.generate(ai_news, financial_news)
                # 保存业务建议
                self._save_business_ideas(business_ideas)
            logger.info(f"生成了 {len(business_ideas)} 条业务建议")

            # 5. 生成报告
            logger.info("[5/6] 开始生成报告...")
            report = self.formatter.format(ai_news, financial_news, blog_recommendations, business_ideas)
            simple_report = self.formatter.format_simple(ai_news, financial_news, blog_recommendations, business_ideas, self.translator)
            logger.info(f"推送报告预览:\n{simple_report[:1000]}")

            # 保存报告
            self._save_report(report, ai_news, financial_news, blog_recommendations, business_ideas)
            logger.info("报告生成完成")

            # 6. 推送
            logger.info("[6/6] 开始推送...")
            success = self.publisher.publish(simple_report)
            if success:
                logger.info("推送成功!")
            else:
                logger.warning("推送失败，已保存到本地")

            # 保存报告到本地文件
            self._save_report_to_local(simple_report)

            logger.info("=" * 50)
            logger.info("AI Daily Pulse 运行完成")
            logger.info("=" * 50)

            return True

        except Exception as e:
            logger.error(f"运行出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _save_data(self, ai_news: list, financial_news: list, blog_recommendations: list):
        """保存数据到数据库"""
        # 保存AI资讯
        for item in ai_news:
            self.db.add_news_item({
                "source": item.get("source"),
                "source_name": item.get("source_name"),
                "title": item.get("title"),
                "url": item.get("url"),
                "summary": item.get("summary"),
                "content": item.get("content"),
                "author": item.get("author"),
                "published_at": item.get("published_at"),
                "category": item.get("category"),
                "is_financial": False,
                "keywords": item.get("keywords", ""),
            })

        # 保存金融AI资讯
        for item in financial_news:
            self.db.add_news_item({
                "source": item.get("source"),
                "source_name": item.get("source_name"),
                "title": item.get("title"),
                "url": item.get("url"),
                "summary": item.get("summary"),
                "content": item.get("content"),
                "author": item.get("author"),
                "published_at": item.get("published_at"),
                "category": item.get("category"),
                "is_financial": True,
                "keywords": item.get("keywords", ""),
            })

        # 保存博客推荐
        for blog in blog_recommendations:
            self.db.add_blog_recommendation({
                "date": blog.get("date", self.today),
                "title": blog.get("title"),
                "url": blog.get("url"),
                "source_author": blog.get("source_author"),
                "summary": blog.get("summary"),
            })

    def _save_business_ideas(self, ideas: list):
        """保存业务建议"""
        # 先清除今日的建议
        self.db.clear_business_ideas_by_date(self.today)

        for i, idea in enumerate(ideas, 1):
            self.db.add_business_idea({
                "date": self.today,
                "idea_number": i,
                "title": idea.get("title"),
                "description": idea.get("description"),
                "difficulty": idea.get("difficulty"),
                "expected_benefit": idea.get("expected_benefit"),
                "source_items": "[]",
            })

    def _save_report(self, report: str, ai_news: list, financial_news: list, blog_recommendations: list, business_ideas: list):
        """保存报告"""
        self.db.add_daily_report({
            "date": self.today,
            "content": report,
            "ai_news_count": len(ai_news),
            "financial_news_count": len(financial_news),
            "blog_recommendations_count": len(blog_recommendations),
            "business_ideas_count": len(business_ideas),
        })

    def _save_report_to_local(self, content: str):
        """保存报告到本地文件"""
        import os
        from pathlib import Path

        # 报告保存目录
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)

        # 文件名：日期.md
        filename = f"{self.today}.md"
        filepath = report_dir / filename

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"报告已保存到本地: {filepath}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="AI Daily Pulse")
    parser.add_argument("--test", action="store_true", help="测试模式（只输出到控制台）")
    args = parser.parse_args()

    # 配置日志
    setup_logging()

    # 创建实例并运行
    app = AIDailyPulse()
    success = app.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
