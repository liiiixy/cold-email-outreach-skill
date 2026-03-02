# Skill: 邮件发送与追踪 (Email Sender)

## 触发条件
当用户提到以下意图时激活：
- "发送邮件"、"发出去"、"send emails"、"批量发送"
- "检查退信"、"追踪邮件"、"查看发送状态"、"track emails"
- outreach-campaign 流程中的第 4 步

## 概述
负责邮件的**配置、发送、退信检测、自动重发、追踪报告**。从一份已确认的发送列表出发，完成从发出到追踪的闭环。

## 被其他 Skill 调用
- **outreach-campaign**（`.claude/skills/outreach-campaign.md`）在第 4 步调用本 skill
- 本 skill 也可被用户直接触发，独立使用

## 前置输入
1. **待发送列表** — `[{"merchant": {...}, "email_content": {"subject": "...", "body": "..."}}, ...]`
   - 通常来自 outreach-campaign 流程，保存在 `/tmp/outreach_send_list.json`
   - 也可由用户直接提供
2. **发件人邮箱凭据** — 用户提供（不会被保存到文件）

## 第 1 步：配置邮件服务

### 推荐 Gmail SMTP（最简单）

1. 用户提供 Gmail 地址（个人或 Google Workspace）
2. 用户前往 [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) 生成 App Password
3. 提供 16 位密码即可

### 其他选项

| 服务 | 免费额度 | 适用场景 |
|------|---------|---------|
| **Gmail SMTP** | 每天500封 | 推荐，无需额外注册 |
| **Resend** | 每天100封/每月3000封 | 需发 HTML 邮件时 |
| **SendGrid** | 每天100封 | 大规模发送 |
| **自定义 SMTP** | 取决于服务商 | 已有邮件服务器 |

使用 `scripts/outreach/email_sender.py` 的 `get_all_provider_options()` 展示选项，`get_setup_guide(provider)` 展示配置步骤。

### 还需确认

> "发送前确认几个信息：
> 1. **发件人显示名** — 收件人看到的发件人名字
> 2. **发件邮箱** — 你的邮箱地址
> 3. **认证凭据** — App Password 或 API Key"

## 第 2 步：发送

使用 `scripts/outreach/email_sender.py` 的 `batch_send()` 逐封发送。

**限流策略**：
- 每封邮件间隔 1-2 秒（避免被邮件服务限流）
- 遇到失败立即记录，不中断剩余发送
- 单封最多重试 2 次

**发送过程实时反馈**：
```
[1/50] Allbirds (hello@allbirds.com): ✅ 发送成功
[2/50] Everlane (team@everlane.com): ✅ 发送成功
[3/50] Bad Brand (fake@bad.com): ❌ 发送失败 - Connection refused
...
```

**发送完成后**，保存发送列表到 `/tmp/outreach_send_list.json`（供追踪使用）。

## 第 3 步：退信检测 + 自动重发

**发送完最后一封后，等待 90 秒**，然后自动执行：

### 3.1 扫描收件箱

使用 `scripts/outreach/inbox_scanner.py` 的 `scan_inbox()` 通过 IMAP 扫描（Gmail SMTP 的 App Password 同样适用于 IMAP）：

```python
from scripts.outreach.inbox_scanner import scan_inbox, classify_responses
inbox = scan_inbox('imap.gmail.com', from_email, app_password, since_hours=24)
```

分类逻辑（由 `classify_responses()` 完成）：
| 类型 | 判断依据 | 处理方式 |
|------|---------|---------|
| 退信 | From 含 `mailer-daemon`/`postmaster` | 提取失败邮箱，尝试重发 |
| 自动回复 | From 域名匹配发送列表 | 标记为已送达 |
| 无关邮件 | 不匹配以上 | 忽略 |

### 3.2 退信自动重发

对每个退信的品牌：
1. 调用 **email-finder skill** 重新查找正确邮箱
2. 找到新邮箱 → 自动重发同一封邮件
3. 重发成功后记录到映射文件：
   ```python
   from scripts.outreach.inbox_scanner import save_retried_emails
   save_retried_emails({"旧邮箱": "新邮箱"})
   ```
4. 找不到 → 标记为"失败"

### 3.3 生成追踪报告

```python
from scripts.outreach.inbox_scanner import (
    classify_responses, generate_tracking_report, export_tracking_excel
)
result = classify_responses(inbox, send_list)
print(generate_tracking_report(result))
export_tracking_excel(result, send_list, 'contact/Tracking.xlsx')
```

**三种状态**：
| 状态 | 含义 |
|------|------|
| ✅ 已送达 | 收到自动回复，确认送达 |
| ❌ 失败 | 退信且找不到新邮箱 |
| ⏳ 暂无回复 | 正常等待中 |

**关键机制**：`classify_responses()` 自动读取 `/tmp/outreach_retried.json`，静默跳过已修复的退信。用户只看到最终结果。

**Excel 导出**（保存到 `contact/` 目录）：
- Sheet 1「追踪状态」：品牌、邮箱、状态、备注
- Sheet 2「邮件内容」：品牌、邮箱、标题、正文
- Sheet 3「发送摘要」：汇总统计

## 后续建议

追踪报告末尾告知用户：
> "📋 后续建议：
> 1. **1-3 天后** — 调用 [email-followup skill](`.claude/skills/email-followup.md`) 查看回复并智能跟进
> 2. **5-7 天后** — 对暂无回复的品牌发 follow-up
> 3. **持续追踪** — 记录哪些标题/CTA 拿到回复，优化下一轮"

**V2 追踪报告**：使用 `classify_responses_v2()` 和 `generate_tracking_report_v2()` 可区分自动回复和真人回复，支持意图检测（已转内部/转介绍/感兴趣/拒绝）。详见 `email-followup.md`。

## 独立使用场景

### 场景 1：只发送已准备好的邮件
```
用户："我有一个 send_list.json，帮我发出去"
→ 跳过步骤 1 的服务选择（如果之前已配置过），直接发送
```

### 场景 2：只检查退信
```
用户："帮我查一下上次发的邮件有没有退信"
→ 直接进入步骤 3，扫描收件箱 + 生成报告
```

### 场景 3：只重发失败的
```
用户："Fear of God 那封退信了，帮我找新邮箱重发"
→ 调用 email-finder 找新邮箱 → 重发 → 更新追踪
```

## 错误处理

```
认证失败 → "密码可能不正确，请检查 App Password 是否完整复制（16位，含空格）"
发件人未验证 → "Gmail 需要先开启两步验证才能生成 App Password"
限流 → "Gmail 限制了发送频率，建议等 1 小时后继续，或使用 Resend/SendGrid"
网络超时 → "连接超时，检查网络后重试"
```
