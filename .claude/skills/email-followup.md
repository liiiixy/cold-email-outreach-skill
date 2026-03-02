# Skill: 邮件追踪与智能跟进 (Email Follow-up)

## 触发条件
当用户提到以下意图时激活：
- "查看回复"、"有没有人回"、"check replies"、"追踪进度"
- "跟进邮件"、"follow up"、"发 follow-up"
- "昨天发的邮件怎么样了"
- outreach-campaign 流程中的第 5 步

## 概述
发送后的闭环管理：**扫描收件箱 → 智能分类回复 → 分析每封回复的意图 → 针对性撰写跟进邮件 → 用户确认后发送**。

核心价值：不是简单地报告"有 X 封回复"，而是**读懂每封回复的意思，给出合理的下一步建议**。

## 被其他 Skill 调用
- **outreach-campaign**（`.claude/skills/outreach-campaign.md`）在第 5 步调用本 skill
- 也可由用户直接触发

## 前置条件
1. `/tmp/outreach_send_list.json` — 发送记录（知道发给了谁）
2. `/tmp/outreach_retried.json` — 已修复退信记录（可选）
3. 邮箱 IMAP 凭据（Gmail App Password 同时支持 SMTP 和 IMAP）

## 工作流程

### 第 1 步：扫描收件箱

使用 `scripts/outreach/inbox_scanner.py` 扫描最近 48-72 小时的收件箱邮件。

```python
from scripts.outreach.inbox_scanner import scan_inbox
inbox = scan_inbox('imap.gmail.com', email, password, since_hours=72)
```

### 第 2 步：智能分类回复

将每封相关邮件分为 **4 类**（不是之前的 3 类）：

| 分类 | 判断依据 | 示例 |
|------|---------|------|
| **bounce** 退信 | From 含 `mailer-daemon`/`postmaster` | "Address not found" |
| **auto_reply** 自动回复 | 模板化内容、含工单号、标准客服话术 | "We will respond within 24-48 hours" |
| **human_reply** 真人回复 | 有具体内容/建议/提问/转介绍 | "Please contact our PR team at..." |
| **no_response** 暂无回复 | 收件箱中无匹配邮件 | — |

#### 自动回复 vs 真人回复的判断规则

**自动回复特征**（命中 2 个以上判定为自动回复）：
- 包含 "We have received your email/inquiry"
- 包含 "will respond within X hours/days"
- 包含 "This is an automated response"
- 包含工单号模式（如 `[#12345]`、`Ticket ID: XXX`）
- 包含标准客服信息（营业时间、FAQ 链接、退换货政策）
- 发送时间与我们发出的时间差 < 5 分钟（即时自动回复）
- 发件人是通用地址（support@、help@、info@、customercare@）

**真人回复特征**（命中 1 个以上判定为真人回复）：
- 提到具体的人名或部门（"forwarded to our relevant department"、"contact our Press team"）
- 给出了新的联系方式或转介绍邮箱
- 对我们的产品/提议有实质性回应
- 提出了具体问题
- 发送时间与我们发出的时间差 > 1 小时（人工处理后回复）
- 有个人签名（具体人名 + 职位）

### 第 3 步：分析意图 + 建议下一步

对每封回复，判断意图并建议行动：

| 意图 | 示例 | 建议行动 |
|------|------|---------|
| **已转内部** | "forwarded to relevant department" | 发 thank you + 补充信息，等待 |
| **转介绍** | "contact our PR team at xxx@xxx.com" | 给新联系人发邮件，提及是客服推荐来的 |
| **感兴趣** | "Tell me more" / "Can you demo?" | 立即回复，安排 demo |
| **礼貌拒绝** | "Not interested at this time" | 感谢 + 标记不再跟进 |
| **自动确认** | "We received your email" | 等 2-3 个工作日，没人工回复则 follow-up |
| **暂无回复** | — | 3-5 天后发 follow-up（更短、不同角度） |

### 第 4 步：撰写跟进邮件

根据分类和意图，为需要跟进的品牌撰写邮件：

#### 4.1 Thank You Letter（针对"已转内部"）
- 回复原邮件线程（保持 Subject + In-Reply-To）
- 感谢对方转发
- 简短补充 1-2 句核心价值
- 表示不急，随时可以聊

#### 4.2 转介绍邮件（针对"转介绍"）
- 发送到新邮箱
- 开头提及是谁推荐的（"Your customer team pointed me this way"）
- 重新简述产品价值，针对新联系人的角色调整措辞
- 明确 ask（10 分钟 demo / 快速看一下）

#### 4.3 Follow-up（针对"暂无回复"，发送时机：3-7 天后）
- 回复原邮件线程
- 更短（2-3 句）
- 换一个角度或加一个新信息点
- 不要重复第一封的内容

#### 4.4 感兴趣回复（针对"感兴趣"）
- 立即回复
- 直接回答对方的问题
- 提供 demo 链接或安排时间

**交互节点（绝对不能跳过）**：
> "以下是建议发送的跟进邮件：
>
> **[真人回复 - 需要跟进]**
> 1. Brand A — Thank you letter（已转内部）
> 2. Brand B — 新邮件给 PR 团队（转介绍）
>
> **[暂无回复 - 建议 X 天后 follow-up]**
> 3. Brand C — Follow-up
> ...
>
> 你可以：
> 1. ✅ 全部确认发送
> 2. ✏️ 修改某封
> 3. 🗑️ 跳过某封
> 4. ⏰ 改变发送时间
>
> 确认后发送。"

### 第 5 步：发送跟进邮件

- 使用 `scripts/outreach/email_sender.py` 发送
- 对回复线程的邮件，设置 `In-Reply-To` 和 `References` header
- 发送后更新追踪数据

### 第 6 步：更新追踪报告

更新 `/tmp/outreach_tracking.json`，记录完整追踪历史：

```json
{
  "brand": "Toast",
  "email": "contact@toa.st",
  "timeline": [
    {"action": "sent", "date": "2026-02-28", "subject": "..."},
    {"action": "auto_reply", "date": "2026-02-28", "summary": "ticket created"},
    {"action": "human_reply", "date": "2026-03-01", "summary": "forwarded to department, Vicky replied"},
    {"action": "followup_sent", "date": "2026-03-02", "subject": "Re: ..."}
  ],
  "status": "engaged",
  "next_action": "wait for department response"
}
```

**状态定义**：
| 状态 | 含义 |
|------|------|
| `sent` | 已发送，等待回复 |
| `auto_replied` | 收到自动回复，确认送达 |
| `engaged` | 有真人互动，积极跟进中 |
| `referred` | 被转介绍到新联系人 |
| `declined` | 对方明确拒绝 |
| `bounced` | 退信 |
| `no_response` | 多次跟进无回复 |

## 追踪报告输出

终端展示清晰的分层报告：

```
============================================================
📊 OUTREACH 追踪报告（含跟进分析）
============================================================
总计发送: 50 封 | 送达率: 96%

⭐ 真人回复 (2) — 需要跟进
------------------------------------------------------------
  Toast              contact@toa.st         已转内部（Vicky）
  Todd Snyder        support@toddsnyder...  转介绍 → PR team

📬 自动回复 (10) — 等待人工回复
------------------------------------------------------------
  Rowing Blazers     hello@rowingblazers... 48-72h 内回复
  ...

⏳ 暂无回复 (36) — 建议 3-5 天后 follow-up
------------------------------------------------------------
  ...

❌ 退信 (2) — 已修复重发
------------------------------------------------------------
  ...
============================================================
```

## 多轮跟进策略

| 轮次 | 时机 | 策略 |
|------|------|------|
| 第 1 轮（本 skill） | 发送后 1-3 天 | 处理回复 + thank you + 转介绍 |
| 第 2 轮 | 发送后 5-7 天 | 对无回复的发 follow-up（换角度） |
| 第 3 轮 | 发送后 14 天 | 最后一次 "break-up email"，提供退出选项 |

每轮都经过本 skill 的完整流程：扫描 → 分类 → 分析 → 撰写 → 确认 → 发送。

## 中间数据存储

| 文件 | 内容 |
|------|------|
| `/tmp/outreach_send_list.json` | 原始发送列表 |
| `/tmp/outreach_retried.json` | 退信修复记录 |
| `/tmp/outreach_tracking.json` | 完整追踪历史（本 skill 新增） |

## 独立使用场景

### 场景 1：查看回复
```
用户："帮我看一下昨天发的邮件有没有人回"
→ 执行步骤 1-3，展示分类报告 + 建议
```

### 场景 2：发 follow-up
```
用户："给没回复的人发 follow-up"
→ 执行步骤 3-5，只针对 no_response 的品牌
```

### 场景 3：处理特定回复
```
用户："Todd Snyder 让我联系 PR，帮我发"
→ 执行步骤 4-5，只处理指定品牌
```

## 错误处理

```
IMAP 连接失败 → "无法连接收件箱，请检查 App Password 是否正确"
无发送记录 → "没有找到发送记录（/tmp/outreach_send_list.json），请先发送邮件或提供发送列表"
凭据过期 → "App Password 可能已失效，请重新生成"
```
