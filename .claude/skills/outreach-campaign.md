# Skill: 商家外展邮件自动化 (Outreach Campaign)

## 触发条件
当用户提到以下关键词时激活此 skill：
- "发邮件"、"外展"、"outreach"、"cold email"、"开发信"
- "批量发送"、"邮件营销"、"联系商家"
- "商家列表"、"品牌列表" + 发邮件相关意图

## 概述
帮助用户从一份商家列表出发，完成从筛选目标客户到批量发送个性化邮件的完整流程。整个过程分 7 步，每步都有明确的用户交互节点。

## 重要原则
- 用户可能是非技术背景，所有操作指引必须清晰具体
- 任何可能产生费用的操作必须提前告知
- 发送前必须让用户确认，绝不能静默群发
- 合规提醒：提醒用户 CAN-SPAM / GDPR 注意事项

## 依赖的 Skill
- **email-finder**（`.claude/skills/email-finder.md`）：邮箱补全环节（第 3 步）调用此 skill 的三层递进策略（WebSearch → WebFetch → 浏览器）。也可被用户单独触发。
- **email-copywriter**（`.claude/skills/email-copywriter.md`）：邮件撰写环节（第 4 步）调用此 skill 的冷邮件写作原则和个性化策略。以点击率和建联转化为目标。也可被用户单独触发。

## 工具模块
所有 Python 模块位于 `scripts/outreach/` 目录：
- `input_parser.py` - 文件解析
- `lead_scorer.py` - 评分辅助
- `email_finder.py` - 邮箱提取（第 1 轮快速扫描用）
- `email_generator.py` - 邮件生成
- `email_sender.py` - 邮件发送
- `reporter.py` - 报告生成

## 工作流程

### 第 1 步：读取商家列表

**触发**：用户提供 Excel/CSV 文件路径

**操作**：
```bash
python3 scripts/outreach/input_parser.py "<文件路径>"
python3 scripts/outreach/input_parser.py "<文件路径>" --summary
```

**输出给用户**：
- 解析到多少条商家记录
- 识别到哪些字段
- 有多少已有邮箱、多少需要补全
- 展示前 3-5 条示例数据让用户确认格式对不对

**如果解析失败**：
- 文件不存在 → 提示用户检查路径
- 格式不支持 → 说明支持 .csv 和 .xlsx
- 缺少 openpyxl → 提示运行 `pip3 install openpyxl`
- 编码问题 → 尝试不同编码，告知用户

**需要用户提供**：
1. 商家列表文件路径
2. 用户的产品/服务描述（用于后续筛选和邮件生成）

---

### 第 2 步：AI 筛选与优先级排序

**前提**：已有商家列表 + 用户产品描述

**操作**：
1. 用 `lead_scorer.py` 的 `prepare_scoring_batch()` 准备商家摘要
2. 用 `build_scoring_prompt()` 生成评分 prompt
3. 用 Claude 自身能力对每批商家做评分（直接在对话中处理，不需要外部 API 调用）
4. 用 `parse_scoring_result()` 解析结果
5. 用 `merge_scores()` 合并回商家列表

**输出给用户**：
用 `format_scoring_report()` 展示三档分组结果：
- 🟢 高优（X 个）：列出商家名 + 理由
- 🟡 中优（X 个）：列出商家名 + 理由
- 🔴 不推荐（X 个）：列出商家名 + 理由

**交互节点**：
> "以上是 AI 的初步筛选结果。你可以：
> 1. 确认这个分组，继续下一步
> 2. 调整某些商家的优先级（告诉我哪些需要调整）
> 3. 修改筛选标准（补充产品描述信息）
>
> 请问怎么处理？"

**注意**：
- 如果商家数量超过 20 个，分批处理（每批 20 个）
- 评分是 Claude 在对话中直接完成的，不需要额外 API 调用

---

### 第 3 步：邮箱补全

> **本步骤调用 [email-finder skill](`.claude/skills/email-finder.md`) 完成。**
> 具体的查找策略、优先级排序、质量验证规则均定义在 email-finder skill 中，此处不重复。

**前提**：用户确认了目标商家列表（通常只处理高优和中优）

**操作**：按 email-finder skill 的策略，对列表中缺少邮箱的商家逐个查找。将已有的 contact_url、website、brand_name 等信息传递给 email-finder 流程。

**交互节点**：完成后向用户汇报结果（找到 X 个、未找到 Y 个），让用户选择：
> 1. 确认，继续下一步
> 2. 手动补充缺失的邮箱
> 3. 跳过没有邮箱的商家

---

### 第 4 步：AI 生成个性化邮件

> **本步骤调用 [email-copywriter skill](`.claude/skills/email-copywriter.md`) 完成。**
> 冷邮件的写作原则、标题公式、正文结构、个性化层级、批量生成策略均定义在 email-copywriter skill 中，此处不重复。

**前提**：有邮箱的商家列表 + 用户产品描述

**先询问用户**：
> "在生成邮件之前，我需要确认几个信息：
> 1. **发件人姓名和公司名**是什么？（会出现在邮件签名中）
> 2. **邮件语言**：英文还是中文？
> 3. 你有没有**邮件模板或特殊要求**？（比如语气、重点、要包含的信息）
>    - 如果没有，我会按照 email-copywriter skill 的原则，为每个收件人深度研究后撰写个性化邮件

**操作**：按 email-copywriter skill 的原则，为每个收件人单独研究、单独撰写：
- 每封邮件前先研究收件人（网站、社交、新闻），找到具体的观察点
- 标题 3-7 词，像同事发来的，不像营销邮件
- 正文 4-5 句话，<100 词，第一句引用对收件人的具体研究发现
- CTA 极轻，允许拒绝（"If the timing's off, no worries at all."）
- 签名简洁：`— {发件人名}, {公司名}`

---

### 第 5 步：用户确认发送列表

**操作**：展示待发送列表

**输出格式**（对每封邮件）：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 收件商家: [商家名]
📨 收件邮箱: [邮箱]
📝 邮件标题: [标题]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[邮件正文]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

如果数量多（>10封），先展示汇总表格（商家名 + 邮箱 + 标题），然后问用户是否要看完整内容。

**交互节点**：
> "以上是待发送的 X 封邮件。你可以：
> 1. ✅ 全部确认，开始发送
> 2. ✏️ 修改某封邮件（告诉我第几封，怎么改）
> 3. 🗑️ 删除某封邮件（告诉我第几封）
> 4. 🔄 重新生成某封邮件
>
> 确认后就会实际发送，请仔细检查。"

**绝对不能跳过这一步。**

---

### 第 6 步：配置邮件服务并发送

**在发送前，先确认邮件服务**：

推荐使用 **Gmail SMTP + App Password**（无需域名验证，无需注册第三方服务）：
1. 用户提供发件邮箱（如 `leah@srp.one`，需为 Google Workspace 账户）
2. 用户前往 [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) 生成 App Password
3. 提供 16 位密码即可开始发送

如果用户偏好其他服务：
| 服务 | 免费额度 | 适用场景 |
|------|---------|---------|
| **Gmail SMTP** | 每天500封 | 推荐，无需额外注册 |
| **Resend** | 每天100封/每月3000封 | 后续需发 HTML 邮件时推荐 |
| **SendGrid** | 每天100封 | 大规模发送 |
| **自定义SMTP** | 取决于服务商 | 已有邮件服务器 |

**发送操作**：
使用 `scripts/outreach/email_sender.py` 中的 `send_via_smtp()` 或对应服务的函数，逐封发送。

**限流策略**：
- 每封邮件间隔 1-2 秒（避免 Gmail 限流）
- 遇到失败立即记录，不中断剩余发送

---

### 第 7 步：收件箱扫描 + 退信自动重发 + 追踪报告

**核心流程**：发送完最后一封邮件后，**等待 90 秒**，然后自动执行以下三步：

#### 7.1 扫描收件箱

使用 IMAP 连接发件邮箱（Gmail SMTP 的 App Password 同样适用于 IMAP），扫描发送后收到的所有邮件：

```python
import imaplib, email
from email.header import decode_header

imap = imaplib.IMAP4_SSL('imap.gmail.com')
imap.login(from_email, app_password)
imap.select('INBOX')
# 搜索今天的邮件
status, messages = imap.search(None, f'(SINCE "{today}")')
```

将收到的邮件分为三类：
| 类型 | 判断依据 | 处理方式 |
|------|---------|---------|
| **退信 (Bounced)** | From 包含 `mailer-daemon` 或 `postmaster`，Subject 包含 `Delivery Status Notification (Failure)` | 提取失败的邮箱地址，自动重跑 |
| **自动回复 (Auto-reply)** | Subject 包含 `Re:` / `Thank you` / `received` / `ticket`，From 域名匹配发送列表中的品牌 | 标记为已送达 |
| **无关邮件** | 不匹配以上规则 | 忽略 |

#### 7.2 退信自动重发

对每个退信的品牌：
1. 调用 **email-finder skill**（`.claude/skills/email-finder.md`）重新查找正确邮箱
2. 如果找到新邮箱 → 自动用新邮箱重发同一封邮件
3. 重发成功后，**立即记录到 retried 映射**：
   ```python
   from scripts.outreach.inbox_scanner import save_retried_emails
   save_retried_emails({"旧邮箱": "新邮箱"})
   # 例: save_retried_emails({"nshop@fearofgod.com": "info@fearofgod.com"})
   ```
   这样后续再次扫描收件箱时，这些旧退信不会被重复报告
4. 如果找不到 → 标记为"需人工处理"

#### 7.3 生成追踪报告

使用 `scripts/outreach/inbox_scanner.py` 的函数自动生成追踪表格（终端 + Excel）：

```python
from scripts.outreach.inbox_scanner import (
    scan_inbox, classify_responses, generate_tracking_report, export_tracking_excel
)

# 1. 扫描收件箱
inbox = scan_inbox('imap.gmail.com', from_email, app_password, since_hours=24)

# 2. 分类（自动读取 /tmp/outreach_retried.json 排除已修复退信）
send_list = json.load(open('/tmp/outreach_send_list.json'))
result = classify_responses(inbox, send_list)

# 3. 终端报告
print(generate_tracking_report(result))

# 4. Excel 导出
export_tracking_excel(result, send_list, 'contact/Tracking.xlsx')
```

**报告三种状态**：
| 状态 | 含义 |
|------|------|
| ✅ 已送达 | 收到自动回复，确认送达 |
| ❌ 失败 | 退信且找不到新邮箱 |
| ⏳ 暂无回复 | 正常等待中 |

**关键机制**：`classify_responses()` 会自动读取 `/tmp/outreach_retried.json`（由 7.2 步保存），静默跳过已修复的退信。重发后的新邮箱按正常流程归类（收到自动回复 → 已送达，否则 → 暂无回复），用户只看到最终结果。

**Excel 导出**（保存到 `contact/` 目录）：
- Sheet 1「追踪状态」：品牌、邮箱、发送状态（送达/退信/暂无回复）、自动回复内容摘要、备注
- Sheet 2「邮件内容」：品牌、邮箱、标题、正文（完整记录）
- Sheet 3「发送摘要」：汇总统计

**后续建议**（在报告末尾告知用户）：
> "📋 后续建议：
> 1. **3-5 天后** — 再扫一次收件箱，查看正式回复
> 2. **1 周后** — 对暂无回复的品牌发 follow-up（第二封更短，2-3 句）
> 3. **持续追踪** — 记录哪些标题/CTA 拿到回复，优化下一轮"

---

## 合规提醒（在流程开始时告知用户）

> "📋 **合规提醒**（CAN-SPAM / GDPR）：
>
> 1. **真实身份**：发件人信息需真实，不能伪造
> 2. **邮件内容**：标题不能误导，需与内容相关
> 3. **收件人同意**：B2B 冷邮件在多数地区合法，但如果收件人要求停止，必须尊重
> 4. **数据保护**：收集的邮箱仅用于本次外展，不要分享给第三方"

## 错误处理与用户引导

### 依赖缺失
```
如果报错 "No module named 'openpyxl'"：
→ "需要安装一个读取 Excel 的工具，运行这个命令即可：
   pip3 install openpyxl"

如果报错 "No module named 'requests'"：
→ "需要安装网络请求工具，运行：
   pip3 install requests beautifulsoup4"
```

### 邮件服务配置失败
```
认证失败 → "API Key 可能不正确，请检查是否完整复制。要重新输入吗？"
发件人未验证 → "需要先验证发件人邮箱。[提供具体步骤]"
```

### 网络问题
```
请求超时 → "网站响应太慢，跳过这个商家继续处理其他的"
被封禁 → "该网站限制了访问，建议手动查找邮箱"
```

## 中间数据存储

所有中间数据保存在 `/tmp/outreach_*` 文件中：
- `/tmp/outreach_merchants.json` - 解析后的商家列表
- `/tmp/outreach_merchants_scored.json` - 带评分的商家列表
- `/tmp/outreach_merchants_with_email.json` - 补全邮箱后的列表
- `/tmp/outreach_send_list.json` - 待发送列表（商家+邮件内容）
- `/tmp/outreach_results.json` - 发送结果
- `/tmp/outreach_report.json` - 最终报告

这样如果中途中断可以从断点继续。

## 快速开始示例对话

用户："我有一份商家列表，想给他们发邮件推广我们的产品"

Claude 回复：
> 好的！我来帮你完成商家外展邮件的全流程。开始之前需要两样东西：
>
> 1. **商家列表文件**：支持 Excel (.xlsx) 或 CSV 格式。请告诉我文件路径。
> 2. **你的产品/服务描述**：简要说明你们做什么、目标客户是谁、核心优势是什么。
>
> 有了这两样，我会帮你：
> - 筛选最匹配的目标商家
> - 自动查找缺失的联系邮箱
> - 为每个商家生成个性化邮件
> - 你确认后批量发送
> - 最后生成发送报告
>
> 请先告诉我文件路径和产品描述吧。
