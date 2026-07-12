"""
钉钉机器人推送模块
"""
import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests


def send_dingtalk_markdown(title: str, content: str,
                           webhook_url: str = None,
                           secret: str = None) -> bool:
    """发送钉钉 Markdown 消息"""
    webhook_url = webhook_url or os.environ.get("DINGTALK_WEBHOOK_URL", "")
    secret = secret or os.environ.get("DINGTALK_SECRET", "")

    if not webhook_url:
        print("❌ 错误: 未配置 DINGTALK_WEBHOOK_URL")
        return False

    # 加签
    if secret:
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        separator = "&" if "?" in webhook_url else "?"
        webhook_url = f"{webhook_url}{separator}timestamp={timestamp}&sign={sign}"

    # 钉钉 Markdown 消息最大长度限制
    if len(content) > 18000:
        content = content[:17900] + "\n\n> ⚠ *消息过长已截断*"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title[:20],
            "text": content,
        }
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        result = resp.json()
        if result.get("errcode") == 0:
            print(f"✅ 钉钉推送成功！")
            return True
        else:
            print(f"❌ 钉钉推送失败: {result.get('errmsg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 钉钉推送异常: {e}")
        return False


def send_briefing(markdown_content: str) -> bool:
    """将简报推送到钉钉"""
    print("\n📤 正在推送到钉钉...")
    title = "⚽ 五大联赛转会简报"
    return send_dingtalk_markdown(title, markdown_content)
