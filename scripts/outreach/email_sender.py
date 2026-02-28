"""
email_sender.py - 邮件发送服务

支持多种邮件服务：
1. SendGrid (API Key)
2. Resend (API Key)
3. Gmail SMTP (App Password)
4. 通用 SMTP

包含限流控制、失败重试、发送记录。
"""

import json
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ═══════════════════════════════════════════
# 服务提供商配置指引
# ═══════════════════════════════════════════

PROVIDER_SETUP_GUIDES = {
    "sendgrid": {
        "name": "SendGrid",
        "steps": [
            "1. 访问 https://signup.sendgrid.com/ 注册账号（免费版每天可发100封）",
            "2. 注册后进入 Settings → API Keys",
            "3. 点击 'Create API Key'，选择 'Full Access' 或 'Restricted Access'（至少需要 Mail Send 权限）",
            "4. 复制生成的 API Key（以 SG. 开头），只会显示一次",
            "5. 需要验证发件人邮箱：Settings → Sender Authentication → Single Sender Verification",
            "6. 将 API Key 告诉我即可开始发送",
        ],
        "env_var": "SENDGRID_API_KEY",
        "free_tier": "每天 100 封免费",
    },
    "resend": {
        "name": "Resend",
        "steps": [
            "1. 访问 https://resend.com/signup 注册账号",
            "2. 免费版每天可发 100 封，每月 3000 封",
            "3. 进入 Dashboard → API Keys → Create API Key",
            "4. 复制 API Key（以 re_ 开头）",
            "5. 如果用自己的域名发送，需要在 Domains 页面添加并验证域名",
            "6. 否则可以用 onboarding@resend.dev 作为发件人（仅限测试）",
            "7. 将 API Key 告诉我即可开始发送",
        ],
        "env_var": "RESEND_API_KEY",
        "free_tier": "每天 100 封，每月 3000 封免费",
    },
    "gmail": {
        "name": "Gmail SMTP",
        "steps": [
            "1. 登录你的 Google 账号",
            "2. 访问 https://myaccount.google.com/security",
            "3. 确保已开启两步验证（2-Step Verification）",
            "4. 在安全设置页面找到 'App passwords'（应用专用密码）",
            "5. 选择应用类型为 'Mail'，设备选 'Other'，输入名称如 'Outreach Tool'",
            "6. 复制生成的 16 位密码（格式如 xxxx xxxx xxxx xxxx）",
            "7. 将你的 Gmail 地址和这个应用密码告诉我",
            "⚠️ 注意：Gmail 每天限制发送 500 封（个人账号）或 2000 封（Workspace）",
        ],
        "env_var": "GMAIL_APP_PASSWORD",
        "free_tier": "每天 500 封（个人）/ 2000 封（Workspace）",
    },
    "smtp": {
        "name": "自定义 SMTP",
        "steps": [
            "1. 准备你的 SMTP 服务器信息：",
            "   - SMTP 服务器地址（如 smtp.example.com）",
            "   - 端口号（通常是 587 或 465）",
            "   - 用户名（通常是邮箱地址）",
            "   - 密码",
            "2. 将以上信息告诉我即可",
        ],
        "env_var": None,
        "free_tier": "取决于你的邮件服务商",
    },
}


def get_setup_guide(provider: str) -> str:
    """获取指定服务商的配置指引。"""
    guide = PROVIDER_SETUP_GUIDES.get(provider)
    if not guide:
        return f"不支持的服务商: {provider}"

    lines = [f"## {guide['name']} 配置指引\n"]
    lines.append(f"**免费额度**: {guide['free_tier']}\n")
    lines.append("**配置步骤**:")
    for step in guide["steps"]:
        lines.append(f"  {step}")
    if guide["env_var"]:
        lines.append(f"\n💡 也可以设置环境变量 `{guide['env_var']}` 来避免每次输入")
    return "\n".join(lines)


def get_all_provider_options() -> str:
    """生成所有服务商选项的说明。"""
    lines = ["## 选择邮件发送服务\n"]
    lines.append("以下是支持的邮件发送服务，请选择一个：\n")
    for key, info in PROVIDER_SETUP_GUIDES.items():
        lines.append(f"### {info['name']}")
        lines.append(f"- 免费额度: {info['free_tier']}")
        if key == "sendgrid":
            lines.append("- 推荐用于大规模发送，稳定性好")
        elif key == "resend":
            lines.append("- 开发者友好，接口简洁，新用户推荐")
        elif key == "gmail":
            lines.append("- 无需额外注册，但有较严格的发送限制")
        elif key == "smtp":
            lines.append("- 如果你已有邮件服务器")
        lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════
# 发送引擎
# ═══════════════════════════════════════════

class SendResult:
    """单封邮件发送结果。"""
    def __init__(self, merchant_name: str, email: str, success: bool,
                 error: str = "", message_id: str = ""):
        self.merchant_name = merchant_name
        self.email = email
        self.success = success
        self.error = error
        self.message_id = message_id
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "merchant_name": self.merchant_name,
            "email": self.email,
            "success": self.success,
            "error": self.error,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }


def send_via_sendgrid(
    api_key: str,
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    from_name: str = "",
) -> SendResult:
    """通过 SendGrid API 发送邮件。"""
    if not HAS_REQUESTS:
        return SendResult("", to_email, False, "需要安装 requests: pip3 install requests")

    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    from_obj = {"email": from_email}
    if from_name:
        from_obj["name"] = from_name

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": from_obj,
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code in (200, 201, 202):
            msg_id = resp.headers.get("X-Message-Id", "")
            return SendResult("", to_email, True, message_id=msg_id)
        else:
            return SendResult("", to_email, False, f"HTTP {resp.status_code}: {resp.text[:200]}")
    except requests.RequestException as e:
        return SendResult("", to_email, False, str(e))


def send_via_resend(
    api_key: str,
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    from_name: str = "",
) -> SendResult:
    """通过 Resend API 发送邮件。"""
    if not HAS_REQUESTS:
        return SendResult("", to_email, False, "需要安装 requests: pip3 install requests")

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    from_str = f"{from_name} <{from_email}>" if from_name else from_email

    payload = {
        "from": from_str,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return SendResult("", to_email, True, message_id=data.get("id", ""))
        else:
            return SendResult("", to_email, False, f"HTTP {resp.status_code}: {resp.text[:200]}")
    except requests.RequestException as e:
        return SendResult("", to_email, False, str(e))


def send_via_gmail(
    gmail_address: str,
    app_password: str,
    to_email: str,
    subject: str,
    body: str,
    from_name: str = "",
) -> SendResult:
    """通过 Gmail SMTP 发送邮件。"""
    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{gmail_address}>" if from_name else gmail_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(gmail_address, app_password.replace(" ", ""))
            server.send_message(msg)
        return SendResult("", to_email, True)
    except smtplib.SMTPException as e:
        return SendResult("", to_email, False, str(e))
    except Exception as e:
        return SendResult("", to_email, False, str(e))


def send_via_smtp(
    host: str,
    port: int,
    username: str,
    password: str,
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    from_name: str = "",
    use_tls: bool = True,
) -> SendResult:
    """通过自定义 SMTP 发送邮件。"""
    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=15) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                if use_tls:
                    server.starttls()
                server.login(username, password)
                server.send_message(msg)
        return SendResult("", to_email, True)
    except Exception as e:
        return SendResult("", to_email, False, str(e))


def batch_send(
    send_list: list[dict],
    provider: str,
    config: dict,
    rate_limit: float = 2.0,
    max_retries: int = 2,
) -> list[dict]:
    """
    批量发送邮件。

    参数:
        send_list: [{"merchant": dict, "email_content": {"subject": str, "body": str}}]
        provider: "sendgrid" / "resend" / "gmail" / "smtp"
        config: 服务商配置（API key、邮箱等）
        rate_limit: 每封邮件之间的间隔秒数（防止限流）
        max_retries: 失败重试次数

    返回: [SendResult.to_dict()]
    """
    results = []
    total = len(send_list)

    for i, item in enumerate(send_list):
        merchant = item["merchant"]
        content = item["email_content"]
        name = merchant.get("brand_name", f"商家{i+1}")
        to_email = merchant.get("email")

        if not to_email:
            results.append(SendResult(name, "", False, "无邮箱地址").to_dict())
            print(f"[{i+1}/{total}] {name}: ⚠️ 跳过（无邮箱）")
            continue

        subject = content.get("subject", "")
        body = content.get("body", "")

        # 重试逻辑
        for attempt in range(max_retries + 1):
            if provider == "sendgrid":
                result = send_via_sendgrid(
                    config["api_key"], config["from_email"], to_email,
                    subject, body, config.get("from_name", ""),
                )
            elif provider == "resend":
                result = send_via_resend(
                    config["api_key"], config["from_email"], to_email,
                    subject, body, config.get("from_name", ""),
                )
            elif provider == "gmail":
                result = send_via_gmail(
                    config["gmail_address"], config["app_password"], to_email,
                    subject, body, config.get("from_name", ""),
                )
            elif provider == "smtp":
                result = send_via_smtp(
                    config["host"], config["port"], config["username"],
                    config["password"], config["from_email"], to_email,
                    subject, body, config.get("from_name", ""),
                    config.get("use_tls", True),
                )
            else:
                result = SendResult(name, to_email, False, f"未知服务商: {provider}")
                break

            result.merchant_name = name

            if result.success:
                print(f"[{i+1}/{total}] {name} ({to_email}): ✅ 发送成功")
                break
            elif attempt < max_retries:
                print(f"[{i+1}/{total}] {name}: ⚠️ 发送失败，{attempt+1}/{max_retries} 次重试...")
                time.sleep(rate_limit)
            else:
                print(f"[{i+1}/{total}] {name} ({to_email}): ❌ 发送失败 - {result.error}")

        results.append(result.to_dict())

        # 限流
        if i < total - 1:
            time.sleep(rate_limit)

    return results


# CLI 入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 email_sender.py --providers       # 列出所有服务商")
        print("  python3 email_sender.py --guide <provider> # 某个服务商的配置指引")
        sys.exit(1)

    if sys.argv[1] == "--providers":
        print(get_all_provider_options())
    elif sys.argv[1] == "--guide":
        provider = sys.argv[2] if len(sys.argv) > 2 else "sendgrid"
        print(get_setup_guide(provider))
