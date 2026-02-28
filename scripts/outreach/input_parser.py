"""
input_parser.py - 读取和解析商家列表文件（Excel / CSV）

输出标准化的商家字典列表，字段统一映射。
"""

import csv
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# 尝试导入 openpyxl，不可用时仅支持 CSV
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# 邮箱正则
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# 标准化字段名映射（源文件中的列名 → 内部字段名）
COLUMN_ALIASES = {
    # 商家名
    "brand": "brand_name",
    "brand name": "brand_name",
    "商家名": "brand_name",
    "商家": "brand_name",
    "店铺名": "brand_name",
    "name": "brand_name",
    # 官网
    "website": "website",
    "官网": "website",
    "url": "website",
    "site": "website",
    # Contact 页面
    "contact": "contact_info",
    "contact page": "contact_url",
    "contact url": "contact_url",
    "联系页面": "contact_url",
    # 邮箱
    "email": "email",
    "邮箱": "email",
    "e-mail": "email",
    "mail": "email",
    # 品类
    "categories": "categories",
    "category": "categories",
    "品类": "categories",
    # SKU / 产品数
    "~ # products": "product_count",
    "sku": "product_count",
    "sku数": "product_count",
    "product count": "product_count",
    "产品数": "product_count",
    # 价格档位
    "pricing ($ - $$$$)": "pricing",
    "pricing": "pricing",
    "价格": "pricing",
    # 风格
    "style persona": "style",
    "style": "style",
    "风格": "style",
    # 平台
    "shopify": "shopify",
    # 社媒
    "ig followers": "ig_followers",
    "instagram": "ig_followers",
    # 地区
    "origin or hq location": "location",
    "location": "location",
    "地区": "location",
    # 备注
    "notes": "notes",
    "备注": "notes",
    # 图片类型
    "imagery type": "imagery_type",
    # 视频
    "video on pdp": "has_video",
    # 单品牌/多品牌
    "single/multi-brand": "brand_type",
    # 配饰/鞋
    "accessories/shoes": "has_accessories",
    "assessories/shoes": "has_accessories",
    # 中文列名补充
    "品牌名称": "brand_name",
}


def _normalize_column_name(raw: str) -> str:
    """将原始列名映射到标准字段名。"""
    cleaned = raw.strip().lower()
    return COLUMN_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


def _clean_row(row: dict) -> dict:
    """清理行数据：去除空白、空值统一为 None。"""
    cleaned = {}
    for k, v in row.items():
        if isinstance(v, str):
            v = v.strip()
            if v == "" or v.lower() in ("n/a", "na", "-", "—"):
                v = None
        cleaned[k] = v
    return cleaned


def parse_csv(file_path: str) -> list[dict]:
    """解析 CSV 文件，返回标准化的商家列表。"""
    merchants = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        # 建立列名映射
        col_map = {col: _normalize_column_name(col) for col in reader.fieldnames}
        for row in reader:
            mapped = {col_map[k]: v for k, v in row.items() if k in col_map}
            mapped = _clean_row(mapped)
            # 跳过完全为空的行
            if all(v is None for v in mapped.values()):
                continue
            merchants.append(mapped)
    return merchants


def parse_excel(file_path: str) -> list[dict]:
    """解析 Excel 文件，返回标准化的商家列表。"""
    if not HAS_OPENPYXL:
        raise ImportError(
            "需要安装 openpyxl 来读取 Excel 文件。\n"
            "运行: pip3 install openpyxl"
        )
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 2:
        return []

    # 第一行作为列名
    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    col_map = {h: _normalize_column_name(h) for h in headers}

    merchants = []
    for row in rows[1:]:
        raw = {headers[i]: (row[i] if i < len(row) else None) for i in range(len(headers))}
        mapped = {col_map[k]: v for k, v in raw.items()}
        mapped = _clean_row(mapped)
        if all(v is None for v in mapped.values()):
            continue
        merchants.append(mapped)
    return merchants


URL_REGEX = re.compile(r'https?://[^\s,\n]+')


def _post_process(merchants: list[dict]) -> list[dict]:
    """
    后处理：从 contact_info 字段中提取 URL 和邮箱，填充缺失字段。
    """
    for m in merchants:
        contact_info = m.get("contact_info")
        if not contact_info or not isinstance(contact_info, str):
            continue

        # 从 contact_info 中提取 URL
        urls = URL_REGEX.findall(contact_info)
        for url in urls:
            url_lower = url.lower()
            if not m.get("contact_url") and any(
                kw in url_lower for kw in ["contact", "support", "get-in-touch", "reach"]
            ):
                m["contact_url"] = url
            elif not m.get("website"):
                parsed = urlparse(url)
                m["website"] = f"{parsed.scheme}://{parsed.netloc}"

        # 如果有 contact_url 但没有 website，从 contact_url 提取根域名
        if m.get("contact_url") and not m.get("website"):
            parsed = urlparse(m["contact_url"])
            m["website"] = f"{parsed.scheme}://{parsed.netloc}"

        # 从 contact_info 中提取邮箱
        if not m.get("email"):
            emails = EMAIL_REGEX.findall(contact_info)
            valid = [e for e in emails if _is_valid_email_basic(e)]
            if valid:
                m["email"] = valid[0]

    return merchants


def _is_valid_email_basic(email: str) -> bool:
    """基本邮箱验证（用于 input_parser）。"""
    email = email.lower().strip()
    if len(email) > 254 or len(email) < 5:
        return False
    if any(x in email for x in ["example.com", "sentry.io", ".png", ".jpg", "schema.org", "w3.org"]):
        return False
    return True


def parse_file(file_path: str) -> list[dict]:
    """
    自动识别文件类型并解析。

    返回: 标准化的商家字典列表
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    ext = path.suffix.lower()
    if ext == ".csv":
        merchants = parse_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        merchants = parse_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}（支持 .csv, .xlsx）")

    return _post_process(merchants)


def get_summary(merchants: list[dict]) -> dict:
    """生成商家列表的摘要统计。"""
    total = len(merchants)
    has_email = sum(1 for m in merchants if m.get("email"))
    has_website = sum(1 for m in merchants if m.get("website"))
    has_contact_url = sum(1 for m in merchants if m.get("contact_url"))
    has_contact_info = sum(1 for m in merchants if m.get("contact_info"))

    # 品类分布
    categories = {}
    for m in merchants:
        cat = m.get("categories")
        if cat:
            for c in re.split(r"[,;/、]", str(cat)):
                c = c.strip()
                if c:
                    categories[c] = categories.get(c, 0) + 1

    return {
        "total": total,
        "has_email": has_email,
        "has_website": has_website,
        "has_contact_url": has_contact_url,
        "has_contact_info": has_contact_info,
        "needs_email_lookup": total - has_email,
        "top_categories": dict(sorted(categories.items(), key=lambda x: -x[1])[:10]),
    }


# CLI 入口：python3 input_parser.py <file_path> [--summary] [--json]
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 input_parser.py <文件路径> [--summary] [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    show_summary = "--summary" in sys.argv
    as_json = "--json" in sys.argv

    try:
        merchants = parse_file(file_path)
    except Exception as e:
        print(f"❌ 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    if show_summary:
        summary = get_summary(merchants)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif as_json:
        print(json.dumps(merchants, ensure_ascii=False, indent=2))
    else:
        print(f"共解析 {len(merchants)} 条商家记录")
        # 显示字段列表
        if merchants:
            fields = list(merchants[0].keys())
            print(f"字段: {', '.join(fields)}")
            # 显示前 3 条
            for i, m in enumerate(merchants[:3]):
                print(f"\n--- 商家 {i+1} ---")
                for k, v in m.items():
                    if v is not None:
                        print(f"  {k}: {v}")
