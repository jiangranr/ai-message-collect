"""翻译模块"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from config import config


class Translator:
    """翻译器 - 使用LLM翻译摘要"""

    def __init__(self):
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        """初始化LLM客户端"""
        try:
            from generator.idea_generator import LLMClient
            api_key = config.llm_api_key
            provider = config.llm_provider
            model = config.llm_model
            base_url = config.llm_base_url

            if api_key:
                self.llm = LLMClient(provider=provider, api_key=api_key, model=model, base_url=base_url)
                logger.info("翻译器 LLM 初始化成功")
        except Exception as e:
            logger.warning(f"翻译器 LLM 初始化失败: {e}")

    def translate(self, text: str, target_lang: str = "中文") -> str:
        """翻译文本"""
        if not self.llm or not text:
            return text

        if len(text) < 10:
            return text

        try:
            prompt = f"""请将以下英文内容翻译成中文，要求：
1. 翻译准确、流畅
2. 保持原文的专业术语
3. 如果是技术内容，使用行业内标准翻译
4. 如果摘要不完整，请补充完整

原文内容：
{text}

请直接输出翻译结果，不要有任何解释："""

            messages = [
                {"role": "system", "content": "你是一个专业的AI技术翻译助手，擅长翻译科技新闻和技术内容。"},
                {"role": "user", "content": prompt}
            ]

            result = self.llm.chat(messages, temperature=0.3)
            if result:
                # 移除思考过程（<thinking> 或 <thought> 标签）
                import re
                result = re.sub(r'<thinking>.*?</thinking>', '', result, flags=re.DOTALL)
                result = re.sub(r'<thought>.*?</thought>', '', result, flags=re.DOTALL)
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
                result = result.strip()
                if result:
                    logger.info(f"翻译成功: {text[:30]}...")
                    return result

        except Exception as e:
            logger.warning(f"翻译失败: {e}")

        return text
