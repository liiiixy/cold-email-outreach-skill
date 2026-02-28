# Skill: 智能邮箱查找 (Email Finder)

## 触发条件
当用户提到以下意图时激活：
- "找邮箱"、"找联系方式"、"find email"、"find contact"
- "查一下这个品牌的邮箱"、"帮我找到他们的 email"
- 给出品牌名/URL 列表并要求获取联系邮箱

## 概述
帮用户查找品牌/公司的联系邮箱。采用多层查找策略，从快到慢、从简到复杂，逐层递进，直到找到为止。

## 被其他 Skill 调用
- **outreach-campaign**（`.claude/skills/outreach-campaign.md`）在第 3 步"邮箱补全"中会调用本 skill 的策略
- **email-copywriter**（`.claude/skills/email-copywriter.md`）生成邮件时需要收件人邮箱
- 本 skill 也可被用户直接触发，独立使用

## 查找策略（按优先级）

### 策略 1：Web 搜索（最快最准）
**用 WebSearch 工具** 直接搜索品牌的联系邮箱。

搜索 query 模板：
- `"{品牌名}" contact email`
- `"{品牌名}" site:{已知域名} email`
- `"{品牌名}" wholesale partnership press email`

从搜索结果摘要中直接提取邮箱（很多时候搜索结果就会包含）。

### 策略 2：WebFetch 抓取（处理静态页面）
如果已知 URL，用 **WebFetch 工具** 获取页面内容。

```
WebFetch(url="{contact_page_url}", prompt="Find all email addresses on this page. List every email you can find, and describe what each one is for (e.g. wholesale, press, customer service, general).")
```

尝试的页面顺序：
1. 用户提供的 URL
2. `/pages/contact`
3. `/contact`
4. `/contact-us`
5. `/pages/about`
6. 首页 footer 区域

### 策略 3：浏览器访问（处理 JS 渲染页面）
如果 WebFetch 拿不到（可能是 JS 渲染），用 **浏览器工具** 实际访问页面：

```
1. mcp__Claude_in_Chrome__navigate(url=contact_url)
2. mcp__Claude_in_Chrome__get_page_text() 或 read_page()
3. 从页面文本中提取邮箱
4. 也可以用 find(query="email address") 定位邮箱元素
```

### 策略 4：Python 脚本批量处理
对于有明确 URL 的批量查找，用 `scripts/outreach/email_finder.py`：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts/outreach')
from email_finder import find_emails_from_url, find_emails_from_website
result = find_emails_from_website('https://example.com')
print(result)
"
```

## 核心原则：多邮箱保留

**当一个品牌有多个邮箱时，不要只选一个，应该全部保留并分类。**

### 为什么保留多个
- 不同邮箱对应不同部门，用户的需求可能匹配不同的入口
- 冷邮件发给 wholesale@ 和 marketing@ 回复率可能完全不同
- 同一品牌发 2-3 个相关邮箱（不同人），整体回复率更高
- 让用户自己决定发给谁，或者全发

### 输出格式
每个品牌返回一个邮箱列表，每个邮箱标注用途：

```
✅ J.W. Pei
   wholesale@jwpei.com    [wholesale]  ← 批发/合作
   pr@jwpei.com           [press]      ← 媒体/PR
   customer@jwpei.com     [support]    ← 客服
   admin@jwpei.com        [general]    ← 通用
   → 推荐: wholesale@ 和 pr@（与 B2B 合作最相关）
```

### 邮箱用途分类标签
根据邮箱前缀自动分类：
- `[wholesale]`：wholesale, trade, reseller, stockist, buyer
- `[partnership]`：partnership, collab, affiliate, business, bd
- `[press]`：press, pr, media, editorial
- `[marketing]`：marketing, brand, growth, campaign
- `[general]`：hello, info, contact, team, office
- `[support]`：support, help, service, care, customer
- `[personal]`：firstname@, firstname.lastname@（个人邮箱）

### 推荐逻辑
找到多个邮箱时，给出推荐，但保留全部：
1. 如果用户目的是 **B2B 合作/销售**：推荐 wholesale > partnership > marketing > general
2. 如果用户目的是 **PR/媒体**：推荐 press > marketing > general
3. 如果用户目的 **不明确**：推荐 general > marketing，同时列出其他选项让用户选
4. **永远不要丢弃任何有效邮箱**，即使是 support@ 也保留（有时小品牌只有这一个入口）

## 邮箱质量验证

### 排除无效邮箱
- `xxx@xxx.xxx` 等占位符
- `noreply@`、`no-reply@` 开头的
- 第三方服务邮箱：`*@gist-apps.com`、`*@glood.ai`、`*@shopify.com` 等 Shopify app 邮箱
- 图片文件名误匹配：`*@2x.png`
- schema/标准域名：`*@schema.org`、`*@w3.org`

### 域名匹配检查
- 邮箱域名应该与品牌相关
- 如果找到的邮箱域名与品牌名完全无关 → 标记为可疑，告知用户
- 但不自动丢弃，标记后让用户判断

## 工作流程

### 单个品牌查找
```
用户："帮我找 J.W. Pei 的联系邮箱"

1. WebSearch: "J.W. Pei jwpei.com wholesale partnership press email contact"
   → 提取所有邮箱 + 各自用途
   → 分类标注，给出推荐

2. 如果搜索结果不够完整：
   WebFetch(官网/contact页面 + wholesale页面 + press页面)
   → 补充更多邮箱

3. 汇总去重，按用途分类展示全部
```

### 批量查找
```
1. 先用 Python 脚本快速扫描有 URL 的品牌（策略 4）
2. 对没找到或只找到 1 个的，用 WebSearch 补充（策略 1）
3. 还没找到的，用 WebFetch/浏览器尝试（策略 2/3）
4. 汇总报告：每个品牌列出所有找到的邮箱及分类
```

### 批量结果汇总格式
```
## 邮箱查找结果（X 个品牌）

| 品牌 | 推荐邮箱 | 其他可用邮箱 | 来源 |
|------|---------|------------|------|
| J.W. Pei | wholesale@jwpei.com | pr@, customer@ | WebSearch |
| Toast | contact@toa.st | press@toa.st | WebSearch |
| ... | ... | ... | ... |

找到: X / 总计 Y
单邮箱: A 个 | 多邮箱: B 个 | 未找到: C 个
```

## 注意事项

- 每次网络请求之间间隔 1-2 秒，避免被封
- 搜索引擎是最有效的策略，优先使用
- 浏览器策略最慢但最强，作为最后手段
- 对用户诚实报告每个策略的结果，不要编造邮箱
- 找到的邮箱域名要和品牌匹配，不匹配的要标记告知用户
- **多邮箱全部保留，给推荐但不替用户做最终决定**
