"""推送模块"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

import httpx
from loguru import logger

from config import config


class PushplusPublisher:
    """Pushplus 推送"""

    def __init__(self):
        self.token = config.pushplus_token

    def publish(self, content: str) -> bool:
        """发送到Pushplus"""
        if not self.token:
            logger.warning("Pushplus token 未配置")
            return False

        try:
            url = "http://www.pushplus.plus/send"
            data = {
                "token": self.token,
                "title": f"AI Daily Pulse - {config.get_today_str()}",
                "content": content,
                "template": "markdown"
            }

            response = httpx.post(url, data=data, timeout=30.0)
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 200:
                logger.info("Pushplus 发送成功")
                return True
            else:
                logger.error(f"Pushplus 发送失败: {result}")
                return False

        except Exception as e:
            logger.error(f"Pushplus 发送异常: {e}")
            return False


class EmailPublisher:
    """邮件发布器"""

    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = config.gmail_email
        self.app_password = config.gmail_app_password

    def publish(self, content: str) -> bool:
        """发送邮件"""
        if not self.email or not self.app_password:
            logger.warning("Gmail 配置未完成")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AI Daily Pulse - {config.get_today_str()}"
            msg['From'] = self.email
            msg['To'] = self.email

            text_content = content.replace("**", "").replace("#", "").replace("-", "").replace("[", "").replace("]", "")
            html_content = self._convert_to_html(content)

            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.sendmail(self.email, [self.email], msg.as_string())

            logger.info("邮件发送成功")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def _convert_to_html(self, markdown: str) -> str:
        import re
        html = markdown
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n')
        html = html.replace('**', '<b>', 1).replace('**', '</b>')
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        html = html.replace('- ', '<li>').replace('\n', '</li>\n')
        html = html.replace('\n', '<br>\n')
        return f"<html><body>{html}</body></html>"


class WeChatPublisher:
    """企业微信群机器人"""

    def __init__(self):
        self.webhook_url = config.wechat_webhook_url

    def publish(self, content: str) -> bool:
        if not self.webhook_url:
            logger.warning("企业微信Webhook URL未配置")
            return False

        message = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }

        try:
            response = httpx.post(self.webhook_url, json=message, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("企业微信发送成功")
                return True
            else:
                logger.error(f"企业微信发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"企业微信发送异常: {e}")
            return False


class ConsolePublisher:
    """控制台输出"""

    def publish(self, content: str) -> bool:
        print("\n" + "=" * 50)
        print("今日AI赋能报告")
        print("=" * 50)
        print(content)
        print("=" * 50)
        return True


class Publisher:
    """统一发布入口"""

    def __init__(self):
        # 优先级: Pushplus > Gmail > 企业微信 > 控制台
        if config.pushplus_token:
            self.publisher = PushplusPublisher()
            logger.info("使用 Pushplus 推送")
        elif config.gmail_email and config.gmail_app_password:
            self.publisher = EmailPublisher()
            logger.info("使用邮件推送")
        elif config.wechat_webhook_url:
            self.publisher = WeChatPublisher()
            logger.info("使用企业微信推送")
        else:
            self.publisher = ConsolePublisher()
            logger.info("使用控制台输出（测试模式）")

    def publish(self, content: str) -> bool:
        return self.publisher.publish(content)


__all__ = ["Publisher", "PushplusPublisher", "EmailPublisher", "WeChatPublisher", "ConsolePublisher"]
