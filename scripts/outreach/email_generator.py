"""
email_generator.py - AI 个性化邮件生成

负责：
1. 构建邮件生成 prompt（根据客户信息 + 用户产品描述 + 可选模板）
2. 解析生成结果（标题 + 正文）
3. 批量生成管理

通用模块：不预设任何行业特定字段，透传所有可用信息。
"""

import json
import re
import sys


def build_email_prompt(
    merchant: dict,
    product_description: str,
    template: str | None = None,
    language: str = "en",
    sender_name: str = "",
    sender_company: str = "",
) -> str:
    """
    构建单封邮件的生成 prompt。

    透传客户所有可用字段，不预设哪些字段重要。
    """
    # 透传所有非 None、非内部字段
    merchant_info = []
    skip_keys = {"priority", "score_reason", "_id"}
    for k, v in merchant.items():
        if v is not None and k not in skip_keys and not k.startswith("_"):
            # 将 key 可读化
            display_key = k.replace("_", " ").title()
            merchant_info.append(f"{display_key}: {v}")

    merchant_text = "\n".join(merchant_info) if merchant_info else "无详细信息"

    lang_instruction = "用英文撰写" if language == "en" else "用中文撰写"

    sender_info = ""
    if sender_name or sender_company:
        parts = []
        if sender_name:
            parts.append(f"发件人: {sender_name}")
        if sender_company:
            parts.append(f"公司: {sender_company}")
        sender_info = "\n".join(parts)

    template_section = ""
    if template:
        template_section = f"""
## 邮件模板/要求
请参考以下模板或要求来写邮件，在此基础上做个性化调整：
{template}
"""

    return f"""你是一个专业的 B2B 冷邮件撰写专家。请为以下目标客户撰写一封个性化的冷邮件。

## 我们的产品/服务
{product_description}

{f"## 发件人信息{chr(10)}{sender_info}" if sender_info else ""}

## 目标客户信息
{merchant_text}
{template_section}
## 写作原则
1. {lang_instruction}
2. 标题 3-7 词，像同事发来的，不像营销邮件
3. 正文 4-5 句话，不超过 100 词
4. 第一句：关于对方的具体观察（来自研究，不是泛泛恭维）
5. 第二句：点破他们可能面临的结构性问题
6. 第三句：一句话说你怎么解决（不罗列功能）
7. 第四句：免费 offer，包装成"找反馈"而不是促销
8. 第五句：极轻 CTA，允许对方说不
9. 签名简洁：— {sender_name or "发件人名"}, {sender_company or "公司名"}
10. 纯文本格式，不用 bold、bullet points

请严格按以下 JSON 格式输出，不要加其他说明：
{{"subject": "邮件标题", "body": "邮件正文（用 \\n 表示换行）"}}"""


def parse_email_result(raw_text: str) -> dict | None:
    """解析 AI 生成的邮件结果。"""
    # 尝试直接解析
    try:
        result = json.loads(raw_text)
        if "subject" in result and "body" in result:
            return result
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 块
    json_match = re.search(r'\{[\s\S]*?"subject"[\s\S]*?"body"[\s\S]*?\}', raw_text)
    if json_match:
        try:
            result = json.loads(json_match.group())
            if "subject" in result and "body" in result:
                return result
        except json.JSONDecodeError:
            pass

    # 尝试 ```json 代码块
    code_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_text)
    if code_match:
        try:
            result = json.loads(code_match.group(1))
            if "subject" in result and "body" in result:
                return result
        except json.JSONDecodeError:
            pass

    return None


def format_email_preview(merchant: dict, email_content: dict) -> str:
    """格式化单封邮件预览。"""
    name = merchant.get("brand_name", "未知")
    email = merchant.get("email", "未知邮箱")
    subject = email_content.get("subject", "无标题")
    body = email_content.get("body", "无内容")

    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 收件人: {name}
📨 邮箱: {email}
📝 标题: {subject}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{body}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


def format_batch_preview(send_list: list[dict]) -> str:
    """格式化批量发送预览。"""
    lines = [f"## 待发送邮件预览（共 {len(send_list)} 封）\n"]

    for i, item in enumerate(send_list, 1):
        merchant = item["merchant"]
        content = item["email_content"]
        name = merchant.get("brand_name", "未知")
        email = merchant.get("email", "未知")
        subject = content.get("subject", "无标题")

        lines.append(f"### {i}. {name} ({email})")
        lines.append(f"**标题**: {subject}")
        body = content.get("body", "")
        preview = body[:100] + "..." if len(body) > 100 else body
        lines.append(f"**正文预览**: {preview}")
        lines.append("")

    return "\n".join(lines)


# CLI 入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 email_generator.py --prompt <客户JSON> <产品描述>")
        print("  python3 email_generator.py --parse <AI输出文本>")
        sys.exit(1)

    if sys.argv[1] == "--prompt":
        merchant = json.loads(sys.argv[2]) if sys.argv[2].startswith("{") else json.load(open(sys.argv[2]))
        desc = sys.argv[3] if len(sys.argv) > 3 else "通用产品"
        prompt = build_email_prompt(merchant, desc)
        print(prompt)
    elif sys.argv[1] == "--parse":
        text = sys.argv[2]
        result = parse_email_result(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
