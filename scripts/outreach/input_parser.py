"""
input_parser.py - 读取和解析列表文件（Excel / CSV）

通用解析器：读取所有列，不预设任何字段名。
只做基础的列名清洗和数据标准化，字段含义交由 Claude 判断。
"""

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

URL_REGEX = re.compile(r'https?://[^\s,\n]+')

# 通用列名归一化：只做最基础的映射（品牌名、网站、邮箱）
# 其他列保持原名，由 Claude 自行理解含义
BASIC_ALIASES = {
    # 品牌/名称
    "brand": "brand_name",
    "brand name": "brand_name",
    "name": "brand_name",
    "商家名": "brand_name",
    "商家": "brand_name",
    "品牌名称": "brand_name",
    "品牌": "brand_name",
    "公司名": "brand_name",
    "company": "brand_name",
    "company name": "brand_name",
    # 网站
    "website": "website",
    "url": "website",
    "site": "website",
    "官网": "website",
    # 邮箱
    "email": "email",
    "e-mail": "email",
    "mail": "email",
    "邮箱": "email",
    "联系邮箱": "email",
    # 联系方式
    "contact": "contact_info",
    "contact page": "contact_url",
    "contact url": "contact_url",
    "联系页面": "contact_url",
    # 备注
    "notes": "notes",
    "备注": "notes",
}


def _normalize_column_name(raw: str) -> str:
    """列名归一化：先查基础别名表，否则保持原名（清洗空格）。"""
    cleaned = raw.strip().lower()
    return BASIC_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


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
    """解析 CSV 文件。"""
    merchants = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        col_map = {col: _normalize_column_name(col) for col in reader.fieldnames}
        for row in reader:
            mapped = {col_map[k]: v for k, v in row.items() if k in col_map}
            mapped = _clean_row(mapped)
            if all(v is None for v in mapped.values()):
                continue
            merchants.append(mapped)
    return merchants


def parse_excel(file_path: str) -> list[dict]:
    """解析 Excel 文件。"""
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


def _post_process(merchants: list[dict]) -> list[dict]:
    """后处理：从 contact_info 中提取 URL 和邮箱。"""
    for m in merchants:
        contact_info = m.get("contact_info")
        if not contact_info or not isinstance(contact_info, str):
            continue

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

        if m.get("contact_url") and not m.get("website"):
            parsed = urlparse(m["contact_url"])
            m["website"] = f"{parsed.scheme}://{parsed.netloc}"

        if not m.get("email"):
            emails = EMAIL_REGEX.findall(contact_info)
            valid = [e for e in emails if _is_valid_email_basic(e)]
            if valid:
                m["email"] = valid[0]

    return merchants


def _is_valid_email_basic(email: str) -> bool:
    """基本邮箱验证。"""
    email = email.lower().strip()
    if len(email) > 254 or len(email) < 5:
        return False
    if any(x in email for x in ["example.com", "sentry.io", ".png", ".jpg", "schema.org", "w3.org"]):
        return False
    return True


def parse_file(file_path: str) -> list[dict]:
    """自动识别文件类型并解析。返回所有字段，不做过滤。"""
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
    """生成列表的摘要统计（通用，不预设任何字段）。"""
    total = len(merchants)
    if total == 0:
        return {"total": 0, "fields": [], "has_email": 0}

    # 统计所有出现过的字段
    all_fields = set()
    for m in merchants:
        all_fields.update(k for k, v in m.items() if v is not None)

    # 统计每个字段的填充率
    fill_rates = {}
    for field in sorted(all_fields):
        count = sum(1 for m in merchants if m.get(field) is not None)
        fill_rates[field] = count

    return {
        "total": total,
        "fields": sorted(all_fields),
        "fill_rates": fill_rates,
        "has_email": sum(1 for m in merchants if m.get("email")),
        "has_website": sum(1 for m in merchants if m.get("website")),
    }


# CLI 入口
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
        print(f"共解析 {len(merchants)} 条记录")
        if merchants:
            fields = list(merchants[0].keys())
            print(f"字段: {', '.join(fields)}")
            for i, m in enumerate(merchants[:3]):
                print(f"\n--- 记录 {i+1} ---")
                for k, v in m.items():
                    if v is not None:
                        print(f"  {k}: {v}")
