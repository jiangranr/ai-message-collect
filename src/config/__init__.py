"""配置模块"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            config_path = PROJECT_ROOT / "config.yaml"

        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

    @property
    def schedule(self) -> Dict[str, str]:
        return self._config.get("schedule", {})

    @property
    def schedule_time(self) -> str:
        return self.schedule.get("time", "08:30")

    @property
    def schedule_timezone(self) -> str:
        return self.schedule.get("timezone", "Asia/Shanghai")

    @property
    def publisher(self) -> Dict[str, Any]:
        return self._config.get("publisher", {})

    @property
    def publisher_enabled(self) -> bool:
        return self.publisher.get("enabled", True)

    @property
    def publisher_type(self) -> str:
        return self.publisher.get("type", "wechat")

    @property
    def wechat_webhook_url(self) -> str:
        return self.publisher.get("webhook_url", "") or os.getenv("WECHAT_WEBHOOK_URL", "")

    @property
    def gmail_email(self) -> str:
        return os.getenv("GMAIL_EMAIL", "")

    @property
    def gmail_app_password(self) -> str:
        return os.getenv("GMAIL_APP_PASSWORD", "")

    @property
    def pushplus_token(self) -> str:
        return os.getenv("PUSHPLUS_TOKEN", "")

    def get_today_str(self) -> str:
        from datetime import date
        return date.today().strftime("%Y年%m月%d日")

    @property
    def sources(self) -> Dict[str, Any]:
        return self._config.get("sources", {})

    @property
    def twitter_config(self) -> Dict[str, Any]:
        return self.sources.get("twitter", {})

    @property
    def twitter_enabled(self) -> bool:
        return self.twitter_config.get("enabled", True)

    @property
    def twitter_accounts(self) -> List[str]:
        return self.twitter_config.get("accounts", [])

    @property
    def blog_config(self) -> Dict[str, Any]:
        return self.sources.get("blog_extraction", {})

    @property
    def blog_enabled(self) -> bool:
        return self.blog_config.get("enabled", True)

    @property
    def blog_max_items(self) -> int:
        return self.blog_config.get("max_items", 10)

    @property
    def blog_exclude_domains(self) -> List[str]:
        return self.blog_config.get("exclude_domains", [
            "twitter.com", "youtube.com", "linkedin.com", "t.co", "instagram.com"
        ])

    @property
    def reddit_config(self) -> Dict[str, Any]:
        return self.sources.get("reddit", {})

    @property
    def reddit_enabled(self) -> bool:
        return self.reddit_config.get("enabled", True)

    @property
    def reddit_subreddits(self) -> List[str]:
        return self.reddit_config.get("subreddits", [])

    @property
    def hacker_news_config(self) -> Dict[str, Any]:
        return self.sources.get("hacker_news", {})

    @property
    def hacker_news_enabled(self) -> bool:
        return self.hacker_news_config.get("enabled", True)

    @property
    def techcrunch_config(self) -> Dict[str, Any]:
        return self.sources.get("techcrunch", {})

    @property
    def techcrunch_enabled(self) -> bool:
        return self.techcrunch_config.get("enabled", True)

    @property
    def company_blogs_config(self) -> Dict[str, Any]:
        return self.sources.get("company_blogs", {})

    @property
    def company_blogs_enabled(self) -> bool:
        return self.company_blogs_config.get("enabled", True)

    @property
    def chinese_media_config(self) -> Dict[str, Any]:
        return self.sources.get("chinese_media", {})

    @property
    def chinese_media_enabled(self) -> bool:
        return self.chinese_media_config.get("enabled", True)

    @property
    def ai_news_sources_config(self) -> Dict[str, Any]:
        return self.sources.get("ai_news_sources", {})

    @property
    def ai_news_sources_enabled(self) -> bool:
        return self.ai_news_sources_config.get("enabled", True)

    @property
    def financial_ai_config(self) -> Dict[str, Any]:
        return self.sources.get("financial_ai", {})

    @property
    def financial_ai_enabled(self) -> bool:
        return self.financial_ai_config.get("enabled", True)

    @property
    def filter_config(self) -> Dict[str, Any]:
        return self._config.get("filter", {})

    @property
    def keywords_include(self) -> List[str]:
        return self.filter_config.get("keywords_include", [])

    @property
    def keywords_exclude(self) -> List[str]:
        return self.filter_config.get("keywords_exclude", [])

    @property
    def min_title_length(self) -> int:
        return self.filter_config.get("min_title_length", 8)

    @property
    def categories_config(self) -> Dict[str, Any]:
        return self._config.get("categories", {})

    @property
    def ai_news_categories(self) -> List[Dict[str, Any]]:
        return self.categories_config.get("ai_news", [])

    @property
    def financial_ai_categories(self) -> List[Dict[str, Any]]:
        return self.categories_config.get("financial_ai", [])

    @property
    def generator_config(self) -> Dict[str, Any]:
        return self._config.get("generator", {})

    @property
    def generator_enabled(self) -> bool:
        return self.generator_config.get("enabled", True)

    @property
    def generator_model(self) -> str:
        return self.generator_config.get("model", "gpt-3.5-turbo")

    @property
    def generator_max_ideas(self) -> int:
        return self.generator_config.get("max_ideas", 5)

    @property
    def generator_temperature(self) -> float:
        return self.generator_config.get("temperature", 0.7)

    @property
    def generator_system_prompt(self) -> str:
        return self.generator_config.get("system_prompt", "")

    @property
    def generator_user_prompt_template(self) -> str:
        return self.generator_config.get("user_prompt_template", "")

    @property
    def database_config(self) -> Dict[str, Any]:
        return self._config.get("database", {})

    @property
    def database_path(self) -> str:
        db_path = self.database_config.get("path", "data/pulse.db")
        return str(PROJECT_ROOT / db_path)

    @property
    def logging_config(self) -> Dict[str, Any]:
        return self._config.get("logging", {})

    @property
    def log_level(self) -> str:
        return self.logging_config.get("level", "INFO")

    @property
    def log_file(self) -> str:
        log_file = self.logging_config.get("file", "logs/app.log")
        return str(PROJECT_ROOT / log_file)

    # Twitter API 配置
    @property
    def twitter_api_key(self) -> str:
        return os.getenv("TWITTER_API_KEY", "")

    @property
    def twitter_api_secret(self) -> str:
        return os.getenv("TWITTER_API_SECRET", "")

    @property
    def twitter_access_token(self) -> str:
        return os.getenv("TWITTER_ACCESS_TOKEN", "")

    @property
    def twitter_access_token_secret(self) -> str:
        return os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    @property
    def twitter_bearer_token(self) -> str:
        return os.getenv("TWITTER_BEARER_TOKEN", "")

    # Reddit API 配置
    @property
    def reddit_client_id(self) -> str:
        return os.getenv("REDDIT_CLIENT_ID", "")

    @property
    def reddit_client_secret(self) -> str:
        return os.getenv("REDDIT_CLIENT_SECRET", "")

    @property
    def reddit_user_agent(self) -> str:
        return os.getenv("REDDIT_USER_AGENT", "AI-Daily-Pulse/1.0")

    # OpenAI 配置 (兼容旧版)
    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # LLM 配置 (新版，支持多提供商)
    @property
    def llm_provider(self) -> str:
        # 优先使用环境变量 LLM_PROVIDER
        env_provider = os.getenv("LLM_PROVIDER", "")
        if env_provider:
            return env_provider

        # 其次使用配置文件
        provider = self.generator_config.get("provider", "")
        if provider:
            return provider

        # 兼容旧版
        if self.openai_api_key:
            return "openai"
        return "openai"

    @property
    def llm_api_key(self) -> str:
        # 优先使用环境变量 LLM_API_KEY
        env_key = os.getenv("LLM_API_KEY", "")
        if env_key:
            return env_key

        # 其次使用配置文件
        key = self.generator_config.get("api_key", "")
        if key:
            return key

        # 兼容旧版
        return self.openai_api_key

    @property
    def llm_model(self) -> str:
        # 优先使用环境变量 LLM_MODEL
        env_model = os.getenv("LLM_MODEL", "")
        if env_model:
            return env_model

        # 其次使用配置文件
        model = self.generator_config.get("model", "")
        if model:
            return model

        # 兼容旧版
        return self.openai_model

    @property
    def llm_base_url(self) -> str:
        return self.generator_config.get("base_url", "") or os.getenv("LLM_BASE_URL", "")


# 全局配置实例
config = Config()
