"""
email_finder.py - 从网页中提取邮箱地址

支持：
1. 直接从 contact 页面 URL 提取
2. 从官网首页出发，尝试常见 contact 路径
3. 提取 mailto 链接、页面文本中的邮箱正则
"""

import json
import re
import sys
import time
from urllib.parse import urljoin, urlparse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# 邮箱正则
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# 需要过滤的无效邮箱模式
INVALID_PATTERNS = [
    r".*@example\.com$",
    r".*@sentry\.io$",
    r".*@.*\.png$",
    r".*@.*\.jpg$",
    r".*@2x\.",
    r"wixpress\.com$",
    r"schema\.org$",
    r"w3\.org$",
    r"googleapis\.com$",
    r"cloudflare",
]

# 常见 contact 页面路径
CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/pages/contact",
    "/pages/contact-us",
    "/about/contact",
    "/get-in-touch",
    "/reach-out",
    "/pages/get-in-touch",
]

# 请求头
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _is_valid_email(email: str) -> bool:
    """过滤无效/垃圾邮箱。"""
    email = email.lower().strip()
    if len(email) > 254 or len(email) < 5:
        return False
    for pattern in INVALID_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return False
    # 过滤明显非邮箱
    local_part = email.split("@")[0]
    if len(local_part) > 64:
        return False
    return True


def _fetch_page(url: str, timeout: int = 10) -> str | None:
    """获取页面 HTML 内容。"""
    if not HAS_REQUESTS:
        raise ImportError("需要安装 requests: pip3 install requests")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException:
        return None


def _extract_emails_from_html(html: str) -> list[str]:
    """从 HTML 中提取邮箱地址。"""
    emails = set()

    # 1. mailto 链接
    if HAS_BS4:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if href.startswith("mailto:"):
                    raw = href.replace("mailto:", "").split("?")[0].strip()
                    if EMAIL_REGEX.match(raw):
                        emails.add(raw.lower())
            # 提取纯文本后做正则匹配
            text = soup.get_text(separator=" ")
        except Exception:
            text = html
    else:
        # 无 BS4 时简单处理
        mailto_matches = re.findall(r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', html)
        for m in mailto_matches:
            emails.add(m.lower())
        text = re.sub(r'<[^>]+>', ' ', html)

    # 2. 正则匹配
    for match in EMAIL_REGEX.findall(text):
        emails.add(match.lower())

    # 3. 也扫描原始 HTML（可能有 JS 中的邮箱）
    for match in EMAIL_REGEX.findall(html):
        emails.add(match.lower())

    # 过滤无效
    return sorted([e for e in emails if _is_valid_email(e)])


def find_emails_from_url(url: str) -> dict:
    """
    从给定 URL 页面提取邮箱。

    返回: {"url": str, "emails": list[str], "status": str}
    """
    html = _fetch_page(url)
    if html is None:
        return {"url": url, "emails": [], "status": "fetch_failed"}

    emails = _extract_emails_from_html(html)
    status = "found" if emails else "no_email_found"
    return {"url": url, "emails": emails, "status": status}


def find_emails_from_website(website: str) -> dict:
    """
    从官网出发，尝试首页和常见 contact 路径。

    返回: {"website": str, "emails": list[str], "tried_urls": list, "status": str}
    """
    # 确保 URL 有协议
    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    all_emails = set()
    tried = []

    # 先试首页
    result = find_emails_from_url(website)
    tried.append({"url": website, "status": result["status"], "found": len(result["emails"])})
    all_emails.update(result["emails"])

    # 如果首页没找到，尝试 contact 路径
    if not all_emails:
        for path in CONTACT_PATHS:
            contact_url = urljoin(website.rstrip("/") + "/", path.lstrip("/"))
            result = find_emails_from_url(contact_url)
            tried.append({"url": contact_url, "status": result["status"], "found": len(result["emails"])})
            all_emails.update(result["emails"])
            if all_emails:
                break  # 找到就停
            time.sleep(0.5)  # 礼貌延迟

    status = "found" if all_emails else "not_found"
    return {
        "website": website,
        "emails": sorted(all_emails),
        "tried_urls": tried,
        "status": status,
    }


def batch_find_emails(merchants: list[dict], delay: float = 1.0) -> list[dict]:
    """
    批量为商家补全邮箱。

    对每个商家：
    - 如果已有 email → 跳过
    - 如果有 contact_url → 从该 URL 提取
    - 如果有 website → 尝试官网和 contact 路径
    - 否则 → 标记为 no_source

    返回: 更新后的商家列表（每个商家增加 email_source 字段）
    """
    results = []
    total = len(merchants)

    for i, merchant in enumerate(merchants):
        name = merchant.get("brand_name", f"商家{i+1}")
        m = dict(merchant)  # 复制

        # 已有邮箱
        if m.get("email"):
            m["email_source"] = "original"
            m["email_lookup_status"] = "already_has_email"
            results.append(m)
            print(f"[{i+1}/{total}] {name}: 已有邮箱 {m['email']}")
            continue

        # 有 contact URL
        contact_url = m.get("contact_url") or m.get("contact_info")
        if contact_url and contact_url.startswith("http"):
            result = find_emails_from_url(contact_url)
            if result["emails"]:
                m["email"] = result["emails"][0]
                m["email_source"] = "contact_page"
                m["email_lookup_status"] = "found"
                m["all_emails_found"] = result["emails"]
                print(f"[{i+1}/{total}] {name}: ✅ 从 contact 页面找到 {m['email']}")
            else:
                # 回退到官网
                website = m.get("website")
                if website:
                    ws_result = find_emails_from_website(website)
                    if ws_result["emails"]:
                        m["email"] = ws_result["emails"][0]
                        m["email_source"] = "website"
                        m["email_lookup_status"] = "found"
                        m["all_emails_found"] = ws_result["emails"]
                        print(f"[{i+1}/{total}] {name}: ✅ 从官网找到 {m['email']}")
                    else:
                        m["email_lookup_status"] = "not_found"
                        print(f"[{i+1}/{total}] {name}: ❌ 未找到邮箱")
                else:
                    m["email_lookup_status"] = "not_found"
                    print(f"[{i+1}/{total}] {name}: ❌ contact 页面未找到，且无官网")
            results.append(m)
            time.sleep(delay)
            continue

        # 只有官网
        website = m.get("website")
        if website:
            ws_result = find_emails_from_website(website)
            if ws_result["emails"]:
                m["email"] = ws_result["emails"][0]
                m["email_source"] = "website"
                m["email_lookup_status"] = "found"
                m["all_emails_found"] = ws_result["emails"]
                print(f"[{i+1}/{total}] {name}: ✅ 从官网找到 {m['email']}")
            else:
                m["email_lookup_status"] = "not_found"
                print(f"[{i+1}/{total}] {name}: ❌ 官网未找到邮箱")
            results.append(m)
            time.sleep(delay)
            continue

        # 没有任何 URL
        m["email_lookup_status"] = "no_source"
        print(f"[{i+1}/{total}] {name}: ⚠️ 无官网或contact页面，无法查找")
        results.append(m)

    return results


# CLI 入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 email_finder.py <URL>              # 从单个URL提取邮箱")
        print("  python3 email_finder.py --website <URL>    # 从官网出发查找")
        print("  python3 email_finder.py --batch <JSON文件>  # 批量查找")
        sys.exit(1)

    if sys.argv[1] == "--website":
        result = find_emails_from_website(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif sys.argv[1] == "--batch":
        with open(sys.argv[2], "r") as f:
            merchants = json.load(f)
        updated = batch_find_emails(merchants)
        print(json.dumps(updated, ensure_ascii=False, indent=2))
    else:
        result = find_emails_from_url(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
