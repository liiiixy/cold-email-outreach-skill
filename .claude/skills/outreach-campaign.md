# Skill: 冷邮件外展自动化 (Outreach Campaign)

## 触发条件
当用户提到以下关键词时激活此 skill：
- "发邮件"、"外展"、"outreach"、"cold email"、"开发信"
- "批量发送"、"邮件营销"、"联系商家"、"联系客户"
- "帮我做一轮 outreach"

## 概述
帮助用户完成从**找到目标客户**到**发送个性化邮件并追踪结果**的完整流程。本 skill 是纯编排器——每一步的具体逻辑由专门的子 skill 负责。

适用于任何产品/服务的冷启动邮件建联，不限行业。

## 重要原则
- 用户可能是非技术背景，所有操作指引必须清晰具体
- 发送前必须让用户确认，绝不能静默群发
- 每一步完成后都有用户交互节点

## 依赖的 Skill
| 步骤 | Skill | 文件 |
|------|-------|------|
| 第 1 步 | lead-researcher | `.claude/skills/lead-researcher.md` |
| 第 2 步 | email-finder | `.claude/skills/email-finder.md` |
| 第 3 步 | email-copywriter | `.claude/skills/email-copywriter.md` |
| 第 4 步 | email-sender | `.claude/skills/email-sender.md` |
| 第 5 步 | email-followup | `.claude/skills/email-followup.md` |

## 工具模块
所有 Python 模块位于 `scripts/outreach/` 目录，由各子 skill 按需调用。

## 工作流程

### 开始前：收集必要信息

> "开始之前，我需要两样东西：
> 1. **你的产品/服务描述**：解决什么问题、目标客户是谁、核心优势
> 2. **客户来源**：Excel/CSV 文件、品牌名列表、URL 列表，或者描述你想联系什么类型的客户
>
> 请告诉我这两个信息。"

---

### 第 1 步：找到目标客户并筛选

> **调用 [lead-researcher skill](`.claude/skills/lead-researcher.md`) 完成。**

- 根据用户提供的客户来源（文件/URL/文字描述），研究并整理目标客户列表
- 根据用户的产品描述，对每个客户做匹配度评分（高优/中优/不推荐）
- 展示筛选结果，让用户确认

**交互节点**：用户确认目标客户列表后进入下一步。

---

### 第 2 步：查找联系邮箱

> **调用 [email-finder skill](`.claude/skills/email-finder.md`) 完成。**

- 对列表中缺少邮箱的客户，按多层策略逐个查找（WebSearch → WebFetch → 浏览器）
- 找到多个邮箱时全部保留，给出推荐

**交互节点**：汇报结果（找到 X 个、未找到 Y 个），让用户选择是否手动补充。

---

### 第 3 步：撰写个性化邮件

> **调用 [email-copywriter skill](`.claude/skills/email-copywriter.md`) 完成。**

**先询问用户**：
> "在生成邮件之前，确认几个信息：
> 1. **发件人姓名和公司名**？
> 2. **邮件语言**：英文还是中文？
> 3. 有没有**邮件模板或特殊要求**？"

- 为每个收件人单独研究、单独撰写（深度个性化）
- 生成后逐封展示预览

**交互节点（绝对不能跳过）**：
> "以上是待发送的 X 封邮件。你可以：
> 1. ✅ 全部确认，开始发送
> 2. ✏️ 修改某封邮件
> 3. 🗑️ 删除某封邮件
> 4. 🔄 重新生成某封邮件
>
> 确认后就会实际发送，请仔细检查。"

---

### 第 4 步：发送 + 追踪

> **调用 [email-sender skill](`.claude/skills/email-sender.md`) 完成。**

- 配置邮件服务（推荐 Gmail SMTP）
- 逐封发送，实时反馈进度
- 发送完成后自动扫描收件箱，检测退信
- 退信自动重发（查找新邮箱 → 重发）
- 生成追踪报告（终端 + Excel）

---

### 第 5 步：追踪回复 + 智能跟进

> **调用 [email-followup skill](`.claude/skills/email-followup.md`) 完成。**

发送后 1-3 天执行（也可由用户随时触发）：

- 扫描收件箱，**区分自动回复和真人回复**
- 分析每封回复的意图（已转内部 / 转介绍 / 感兴趣 / 拒绝）
- 针对性撰写跟进邮件：
  - 真人回复 → thank you letter 或转介绍邮件
  - 暂无回复 → 3-7 天后发 follow-up（更短、换角度）
- 展示跟进邮件预览，用户确认后发送
- 更新追踪报告

**多轮跟进**：
| 轮次 | 时机 | 策略 |
|------|------|------|
| 第 1 轮 | 发送后 1-3 天 | 处理回复 + thank you + 转介绍 |
| 第 2 轮 | 发送后 5-7 天 | 对无回复的发 follow-up |
| 第 3 轮 | 发送后 14 天 | 最后一次 break-up email |

**交互节点**：每封跟进邮件都需用户确认后才发送。

---

## 合规提醒（流程开始时告知用户）

> "📋 **合规提醒**（CAN-SPAM / GDPR）：
> 1. **真实身份**：发件人信息需真实，不能伪造
> 2. **邮件内容**：标题不能误导，需与内容相关
> 3. **收件人同意**：B2B 冷邮件在多数地区合法，但如果收件人要求停止，必须尊重
> 4. **数据保护**：收集的邮箱仅用于本次外展，不要分享给第三方"

## 错误处理

### 依赖缺失
```
缺少 openpyxl → "需要安装 Excel 读取工具: pip3 install openpyxl"
缺少 requests → "需要安装网络工具: pip3 install requests beautifulsoup4"
```

### 网络问题
```
请求超时 → "网站响应太慢，跳过继续处理其他的"
被封禁 → "该网站限制了访问，建议手动查找"
```

## 中间数据存储

所有中间数据保存在 `/tmp/outreach_*` 文件中，中途中断可从断点继续：
- `/tmp/outreach_merchants.json` - 解析后的客户列表
- `/tmp/outreach_merchants_scored.json` - 带评分的客户列表
- `/tmp/outreach_merchants_with_email.json` - 补全邮箱后的列表
- `/tmp/outreach_send_list.json` - 待发送列表（客户+邮件内容）
- `/tmp/outreach_results.json` - 发送结果
- `/tmp/outreach_tracking.json` - 完整追踪历史（含多轮跟进）

## 快速开始示例

用户："我有一份商家列表，想给他们发邮件推广我们的产品"

Claude 回复：
> 好的！开始之前需要两样东西：
>
> 1. **客户来源**：Excel/CSV 文件路径，或者品牌名/URL 列表
> 2. **你的产品/服务描述**：简要说明你们做什么、目标客户是谁、核心优势
>
> 有了这两样，我会帮你：筛选目标客户 → 查找邮箱 → 撰写个性化邮件 → 确认后发送 → 追踪结果
>
> 请先告诉我吧。
