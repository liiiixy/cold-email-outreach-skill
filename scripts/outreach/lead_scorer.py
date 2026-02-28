"""
lead_scorer.py - 商家筛选与优先级排序

根据用户产品描述对商家做相关性判断，输出三档评分。
评分逻辑由 Claude 在 skill 对话中完成，本模块负责：
1. 准备评分所需的商家信息摘要
2. 解析评分结果
3. 按优先级分组排序
"""

import json
import sys


PRIORITY_LABELS = {
    "high": "🟢 高优",
    "medium": "🟡 中优",
    "low": "🔴 不推荐",
}


def prepare_scoring_batch(merchants: list[dict], batch_size: int = 20) -> list[list[dict]]:
    """
    将商家列表拆分为批次，每批生成简洁的摘要供 AI 评分。

    返回: 分批的商家摘要列表
    """
    batches = []
    for i in range(0, len(merchants), batch_size):
        batch = []
        for m in merchants[i:i + batch_size]:
            summary = {
                "brand_name": m.get("brand_name", "未知"),
                "categories": m.get("categories"),
                "style": m.get("style"),
                "pricing": m.get("pricing"),
                "product_count": m.get("product_count"),
                "location": m.get("location"),
                "shopify": m.get("shopify"),
                "ig_followers": m.get("ig_followers"),
                "brand_type": m.get("brand_type"),
                "notes": m.get("notes"),
            }
            # 去除 None 值以减少 token 消耗
            summary = {k: v for k, v in summary.items() if v is not None}
            batch.append(summary)
        batches.append(batch)
    return batches


def build_scoring_prompt(batch: list[dict], product_description: str) -> str:
    """
    构建供 Claude 评分的 prompt。

    返回: 评分 prompt 字符串
    """
    merchants_text = json.dumps(batch, ensure_ascii=False, indent=2)

    return f"""你是一个 B2B 销售匹配专家。请根据以下产品/服务描述，对每个商家做相关性评分。

## 我们的产品/服务
{product_description}

## 待评分商家列表
{merchants_text}

## 评分要求
对每个商家输出：
1. brand_name: 商家名
2. priority: "high" / "medium" / "low"
3. reason: 一句话说明原因（中文）

评分标准：
- high（高优）：产品/品类高度匹配，规模合适，有明确合作潜力
- medium（中优）：有一定匹配度，但可能品类不完全对口或规模不太合适
- low（不推荐）：几乎不匹配，品类无关或明显不适合

请以 JSON 数组格式输出，不要加其他说明：
[{{"brand_name": "xxx", "priority": "high", "reason": "..."}}]"""


def parse_scoring_result(raw_text: str) -> list[dict]:
    """
    解析 AI 返回的评分结果。

    容错处理：尝试从文本中提取 JSON 数组。
    """
    # 尝试直接解析
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 块
    import re
    json_match = re.search(r'\[[\s\S]*?\]', raw_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # 尝试找 ```json 代码块
    code_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', raw_text)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    return []


def merge_scores(merchants: list[dict], scores: list[dict]) -> list[dict]:
    """
    将评分结果合并回商家列表。

    返回: 带有 priority 和 score_reason 字段的商家列表
    """
    score_map = {}
    for s in scores:
        name = s.get("brand_name", "").strip()
        score_map[name.lower()] = s

    result = []
    for m in merchants:
        m = dict(m)
        name = m.get("brand_name", "").strip()
        score = score_map.get(name.lower())
        if score:
            m["priority"] = score.get("priority", "medium")
            m["score_reason"] = score.get("reason", "")
        else:
            m["priority"] = "medium"
            m["score_reason"] = "未评分"
        result.append(m)

    return result


def group_by_priority(merchants: list[dict]) -> dict[str, list[dict]]:
    """按优先级分组。"""
    groups = {"high": [], "medium": [], "low": []}
    for m in merchants:
        p = m.get("priority", "medium")
        if p not in groups:
            p = "medium"
        groups[p].append(m)
    return groups


def format_scoring_report(merchants: list[dict]) -> str:
    """生成评分报告的文本格式。"""
    groups = group_by_priority(merchants)
    lines = []
    total = len(merchants)

    lines.append(f"## 商家筛选结果（共 {total} 个）\n")

    for level in ["high", "medium", "low"]:
        label = PRIORITY_LABELS[level]
        items = groups[level]
        lines.append(f"### {label}（{len(items)} 个）\n")
        if not items:
            lines.append("（无）\n")
            continue
        for m in items:
            name = m.get("brand_name", "未知")
            reason = m.get("score_reason", "")
            cats = m.get("categories", "")
            email_status = "✅ 有邮箱" if m.get("email") else "❌ 无邮箱"
            lines.append(f"- **{name}**（{cats}）{email_status}")
            if reason:
                lines.append(f"  评分理由：{reason}")
        lines.append("")

    return "\n".join(lines)


# CLI 入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 lead_scorer.py --prepare <商家JSON> <产品描述>")
        print("  python3 lead_scorer.py --parse <AI输出文本>")
        print("  python3 lead_scorer.py --report <带评分的商家JSON>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "--prepare":
        with open(sys.argv[2]) as f:
            merchants = json.load(f)
        desc = sys.argv[3] if len(sys.argv) > 3 else "通用产品"
        batches = prepare_scoring_batch(merchants)
        for i, batch in enumerate(batches):
            prompt = build_scoring_prompt(batch, desc)
            print(f"--- Batch {i+1} ({len(batch)} merchants) ---")
            print(prompt)
    elif cmd == "--report":
        with open(sys.argv[2]) as f:
            merchants = json.load(f)
        print(format_scoring_report(merchants))
