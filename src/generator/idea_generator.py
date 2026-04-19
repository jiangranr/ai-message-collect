"""LLM业务建议生成模块"""
import json
import re
from datetime import date
from typing import List, Dict, Any, Optional

from openai import OpenAI
from loguru import logger

from config import config


# 支持的LLM提供商
LLM_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-3.5-turbo",
        "api_base": "https://api.openai.com/v1",
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "default_model": "claude-3-haiku",
        "api_base": "https://api.anthropic.com",
    },
    "qianwen": {
        "name": "阿里云通义千问",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
        "default_model": "qwen-plus",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "zhipu": {
        "name": "智谱清言",
        "models": ["glm-4", "glm-4-flash", "glm-3-turbo"],
        "default_model": "glm-4-flash",
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
    },
    "wenxin": {
        "name": "百度文心一言",
        "models": ["ernie-4.0-8k", "ernie-3.5-8k", "ernie-speed-8k"],
        "default_model": "ernie-3.5-8k",
        "api_base": "https://qianfan.baidubce.com/v2",
    },
    "moonshot": {
        "name": "月之暗面Moonshot",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-8k",
        "api_base": "https://api.moonshot.cn/v1",
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": ["deepseek-chat", "deepseek-coder"],
        "default_model": "deepseek-chat",
        "api_base": "https://api.deepseek.com/v1",
    },
    "minimax": {
        "name": "MiniMax",
        "models": ["MiniMax-Text-01", "MiniMax-M2"],
        "default_model": "MiniMax-Text-01",
        "api_base": "https://api.minimax.chat/v1",
    },
}


class LLMClient:
    """统一的LLM客户端"""

    def __init__(self, provider: str = "openai", api_key: str = "", model: str = "", base_url: str = ""):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        if not self.api_key:
            logger.warning(f"[{self.provider}] API Key 未配置")
            return

        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or LLM_PROVIDERS["openai"]["api_base"])
            elif self.provider == "qianwen":
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or LLM_PROVIDERS["qianwen"]["api_base"])
            elif self.provider == "zhipu":
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or LLM_PROVIDERS["zhipu"]["api_base"])
            elif self.provider == "moonshot":
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or LLM_PROVIDERS["moonshot"]["api_base"])
            elif self.provider == "deepseek":
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or LLM_PROVIDERS["deepseek"]["api_base"])
            elif self.provider == "minimax":
                # MiniMax 需要特殊的 base_url
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or "https://api.minimax.chat/v1")
            else:
                # 默认使用OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or LLM_PROVIDERS["openai"]["api_base"])

            logger.info(f"[{self.provider}] 客户端初始化成功，使用模型: {self.model}")
        except Exception as e:
            logger.error(f"[{self.provider}] 客户端初始化失败: {e}")
            self.client = None

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """发送聊天请求"""
        if not self.client:
            return ""

        try:
            # 针对不同提供商做适配
            extra_kwargs = {}
            if self.provider == "anthropic":
                # Anthropic 需要不同的API格式
                extra_kwargs = {
                    "max_tokens": 4096,
                }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                **extra_kwargs
            )

            content = response.choices[0].message.content
            return content or ""

        except Exception as e:
            logger.error(f"[{self.provider}] 调用失败: {e}")
            return ""


class BusinessIdeaGenerator:
    """业务建议生成器"""

    def __init__(self):
        self.llm = None
        self._init_client()

    def _init_client(self):
        """初始化LLM客户端"""
        # 获取配置
        provider = config.llm_provider  # llm_provider
        api_key = config.llm_api_key  # llm_api_key
        model = config.llm_model  # llm_model
        base_url = config.llm_base_url  # llm_base_url

        if not api_key:
            logger.warning("LLM API Key 未配置")
            return

        provider_info = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["openai"])
        if not model:
            model = provider_info["default_model"]

        self.llm = LLMClient(provider=provider, api_key=api_key, model=model, base_url=base_url)
        logger.info(f"LLM 客户端初始化: {provider_info['name']}")

    def generate(self, ai_news: List[Dict[str, Any]], financial_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成业务建议"""
        if not self.llm or not self.llm.client:
            logger.warning("LLM 客户端未初始化")
            return []

        if not ai_news and not financial_news:
            logger.warning("没有可用的资讯数据")
            return []

        # 构建提示词
        system_prompt = config.generator_system_prompt or self._get_default_system_prompt()
        user_prompt = self._build_user_prompt(ai_news, financial_news)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            content = self.llm.chat(messages, temperature=config.generator_temperature)
            if not content:
                logger.warning("LLM 返回为空")
                return []

            logger.info(f"LLM 响应: {content[:200]}...")

            # 解析响应
            ideas = self._parse_response(content)
            logger.info(f"生成了 {len(ideas)} 条业务建议")

            return ideas

        except Exception as e:
            logger.error(f"生成业务建议失败: {e}")
            return []

    def _get_default_system_prompt(self) -> str:
        """获取默认的系统提示词"""
        return """你是一位深耕金融行业的AI业务顾问，专门为银行后台业务人员提供AI赋能建议。

背景：
- 用户岗位：资金同业交易后台
- 系统类型：静态数据维护系统
- 业务领域：资金业务、KYC/AML、风险管理、运营自动化

要求：
1. 建议必须与银行后台业务直接相关
2. 考虑静态数据维护系统的特点
3. 优先考虑低实施难度、高收益的建议
4. 建议要具体可执行，不能是空泛的概念"""

    def _build_user_prompt(self, ai_news: List[Dict[str, Any]], financial_news: List[Dict[str, Any]]) -> str:
        """构建用户提示词"""
        # 摘要资讯
        ai_summary = self._summarize_news(ai_news, "AI资讯")
        financial_summary = self._summarize_news(financial_news, "金融AI应用")

        template = config.generator_user_prompt_template or """根据以下今日AI资讯和金融AI应用案例，生成{{max_ideas}}条可落地的业务赋能建议。

今日AI资讯摘要：
{ai_news}

金融AI应用案例：
{financial_news}

每个建议包含：
- 建议标题（简洁有力，不超过20字）
- 建议描述（为什么有用、如何落地，50字以内）
- 实施难度（低/中/高）
- 预期收益（量化描述）

请以JSON数组格式输出，每条建议包含：title, description, difficulty, expected_benefit"""

        user_prompt = template.format(
            ai_news=ai_summary,
            financial_news=financial_summary,
            max_ideas=config.generator_max_ideas,
        )

        return user_prompt

    def _summarize_news(self, news: List[Dict[str, Any]], title: str) -> str:
        """摘要资讯"""
        if not news:
            return f"{title}: 无"

        lines = [f"{title}:"]
        for i, item in enumerate(news[:10], 1):  # 最多取10条
            title_text = item.get("title", "")[:100]
            source = item.get("source_name", "")
            lines.append(f"{i}. [{source}] {title_text}")

        return "\n".join(lines)

    def _parse_response(self, content: str) -> List[Dict[str, Any]]:
        """解析LLM响应"""
        ideas = []

        # 尝试提取JSON
        try:
            # 查找JSON数组
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                for item in data:
                    # 新格式
                    if "problem" in item or "solution" in item:
                        ideas.append({
                            "title": item.get("title", ""),
                            "problem": item.get("problem", ""),
                            "solution": item.get("solution", ""),
                            "description": item.get("solution", ""),  # 兼容旧格式
                            "difficulty": item.get("difficulty", "中"),
                            "expected_benefit": item.get("benefit", item.get("expected_benefit", "")),
                        })
                    else:
                        # 旧格式
                        ideas.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "difficulty": item.get("difficulty", "中"),
                            "expected_benefit": item.get("expected_benefit", ""),
                        })
        except json.JSONDecodeError:
            logger.warning("JSON解析失败，尝试文本解析")

        # 如果JSON解析失败，尝试文本解析
        if not ideas:
            ideas = self._parse_text_response(content)

        return ideas[:config.generator_max_ideas]

    def _parse_text_response(self, content: str) -> List[Dict[str, Any]]:
        """文本解析"""
        ideas = []
        lines = content.split("\n")

        current_idea = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 匹配标题
            title_match = re.match(r'^\d+[.、]\s*(.+)', line)
            if title_match:
                if current_idea and current_idea.get("title"):
                    ideas.append(current_idea)
                current_idea = {"title": title_match.group(1).strip()}
                continue

            # 匹配描述
            if "描述" in line or "说明" in line:
                current_idea["description"] = line.split("：")[-1].strip() if "：" in line else line
                continue

            # 匹配难度
            if "难度" in line:
                diff = line.split("：")[-1].strip() if "：" in line else line
                if "低" in diff:
                    current_idea["difficulty"] = "低"
                elif "高" in diff:
                    current_idea["difficulty"] = "高"
                else:
                    current_idea["difficulty"] = "中"
                continue

            # 匹配收益
            if "收益" in line or "效果" in line:
                current_idea["expected_benefit"] = line.split("：")[-1].strip() if "：" in line else line
                continue

        # 添加最后一条
        if current_idea and current_idea.get("title"):
            ideas.append(current_idea)

        return ideas


__all__ = ["BusinessIdeaGenerator", "LLM_PROVIDERS"]
