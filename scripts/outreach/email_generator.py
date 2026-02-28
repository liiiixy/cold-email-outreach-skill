"""
email_generator.py - AI 个性化邮件生成

负责：
1. 构建邮件生成 prompt（根据商家信息 + 用户产品描述 + 可选模板）
2. 解析生成结果（标题 + 正文）
3. 批量生成管理
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

    参数:
        merchant: 商家信息字典
        product_description: 用户产品/服务描述
        template: 可选的邮件模板/要求
        language: 邮件语言 (en/zh)
        sender_name: 发件人姓名
        sender_company: 发件人公司名
    """
    # 商家信息摘要
    merchant_info = []
    if merchant.get("brand_name"):
        merchant_info.append(f"品牌名: {merchant['brand_name']}")
    if merchant.get("categories"):
        merchant_info.append(f"品类: {merchant['categories']}")
    if merchant.get("style"):
        merchant_info.append(f"风格: {merchant['style']}")
    if merchant.get("pricing"):
        merchant_info.append(f"价格档位: {merchant['pricing']}")
    if merchant.get("product_count"):
        merchant_info.append(f"产品数量: {merchant['product_count']}")
    if merchant.get("location"):
        merchant_info.append(f"地区: {merchant['location']}")
    if merchant.get("shopify"):
        merchant_info.append(f"Shopify店铺: {merchant['shopify']}")
    if merchant.get("ig_followers"):
        merchant_info.append(f"Instagram粉丝: {merchant['ig_followers']}")
    if merchant.get("brand_type"):
        merchant_info.append(f"类型: {merchant['brand_type']}")
    if merchant.get("score_reason"):
        merchant_info.append(f"匹配理由: {merchant['score_reason']}")
    if merchant.get("notes"):
        merchant_info.append(f"备注: {merchant['notes']}")

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

    return f"""你是一个专业的 B2B 冷邮件撰写专家。请为以下商家撰写一封个性化的开发信。

## 我们的产品/服务
{product_description}

{f"## 发件人信息{chr(10)}{sender_info}" if sender_info else ""}

## 目标商家信息
{merchant_text}
{template_section}
## 要求
1. {lang_instruction}
2. 邮件标题要吸引注意力，与该商家的业务相关，避免明显的广告感
3. 正文要简洁（150-250词），突出我们的产品如何帮助他们
4. 要体现你了解他们的品牌（引用他们的品类、风格等信息）
5. 包含明确的行动号召（CTA），如安排通话或回复邮件
6. 语气专业但友好，不要过于推销
7. 底部包含退订提示（CAN-SPAM 合规）

请严格按以下 JSON 格式输出，不要加其他说明：
{{"subject": "邮件标题", "body": "邮件正文（用 \\n 表示换行）"}}"""


def parse_email_result(raw_text: str) -> dict | None:
    """
    解析 AI 生成的邮件结果。

    返回: {"subject": str, "body": str} 或 None
    """
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
    name = merchant.get("brand_name", "未知商家")
    email = merchant.get("email", "未知邮箱")
    subject = email_content.get("subject", "无标题")
    body = email_content.get("body", "无内容")

    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 收件商家: {name}
📨 收件邮箱: {email}
📝 邮件标题: {subject}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{body}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


def format_batch_preview(send_list: list[dict]) -> str:
    """
    格式化批量发送预览。

    send_list: [{"merchant": dict, "email_content": dict}, ...]
    """
    lines = [f"## 待发送邮件预览（共 {len(send_list)} 封）\n"]

    for i, item in enumerate(send_list, 1):
        merchant = item["merchant"]
        content = item["email_content"]
        name = merchant.get("brand_name", "未知")
        email = merchant.get("email", "未知")
        subject = content.get("subject", "无标题")

        lines.append(f"### {i}. {name} ({email})")
        lines.append(f"**标题**: {subject}")
        # 正文只显示前 100 字符
        body = content.get("body", "")
        preview = body[:100] + "..." if len(body) > 100 else body
        lines.append(f"**正文预览**: {preview}")
        lines.append("")

    return "\n".join(lines)


# CLI 入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 email_generator.py --prompt <商家JSON> <产品描述>")
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
