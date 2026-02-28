# Skill: 冷邮件撰写 (Email Copywriter)

## 触发条件
- "写邮件"、"写开发信"、"write cold email"、"draft outreach email"
- "优化邮件"、"邮件文案"、"提高回复率"
- outreach-campaign 流程中的第 4 步

## 概述
以**回复率和建联转化**为唯一目标，撰写冷邮件。不是写正式商务函件，不是产品介绍——而是**点破对方正在承受但没精力解决的问题**，让陌生人觉得"这个人懂我，值得回一封"。

本 skill 适用于任何产品/服务的冷启动邮件，不限行业。

## 被其他 Skill 调用
- **outreach-campaign**（`.claude/skills/outreach-campaign.md`）在第 4 步"生成个性化邮件"中调用本 skill
- 本 skill 也可被用户直接触发，独立使用

## 前置输入
开始写邮件前，必须已知：
1. **用户的产品/服务描述** — 解决什么问题、目标客户是谁、核心卖点
2. **发件人姓名和公司名** — 用于签名
3. **收件人信息** — 品牌名、网站、品类、规模等（越多越好）

## 冷邮件核心心态

### ❌ 错误心态：产品介绍
"我们做了一个很棒的产品，来看看吧"
→ 收件人感受：又一封推销邮件

### ✅ 正确心态：问题诊断
"我注意到你有一个结构性问题，很多人都卡在这，有个轻量的解法"
→ 收件人感受：这个人研究过我，而且说的对

### 判断标准
写完邮件后自检：**如果把产品名和公司名删掉，这封邮件还有没有价值？**
- 如果有 → 好邮件（对方能从中得到一个洞察）
- 如果没有 → 产品介绍（对方没有理由回复）

## 邮件撰写规则

### 标题 (Subject Line)
**目标：让收件人点开邮件，仅此而已。**

核心原则：**越不像 pitch 越好**。标题应该像同事或行业朋友随手发来的。

好标题的特征：
- 短（3-7 个词）
- 像内部邮件，不像营销邮件
- 指向对方的**问题**，不是你的**产品**
- 不用全大写、不用感叹号、不用 emoji
- 不提产品名、不提解决方案

标题公式（按场景选用）：
| 场景 | 公式 | 示例 |
|------|------|------|
| 点破问题 | `{他们的痛点}?` | "Managing returns across 5 warehouses?" |
| 轻量提问 | `Quick question about {他们的某件事}` | "Quick question about your checkout flow" |
| 一个想法 | `One thought on {相关话题}` | "One thought on your fulfillment" |
| 个人化 | `{品牌名}, quick question` | "Allbirds, quick question" |
| 观察 | `关于 {你观察到的事}` | "Your new product launch" |

**绝对不用的标题**：
- ❌ "Partnership Opportunity with {公司名}"（太正式、太营销）
- ❌ 任何包含产品功能描述的标题（像 landing page）
- ❌ 包含具体数字承诺的标题（"Boost Your X by 30%!!!"）
- ❌ "Free {产品} for {品牌}"（像广告推送）

### 正文 (Body)
**目标：让收件人觉得 "这个人懂我的处境，值得回一封"。**

#### 结构（总共 4-5 句话）

**第 1 句：观察（关于对方，具体且真实）**
- 提到你注意到他们的什么（规模、品类、网站细节、最近动态）
- 必须具体、可验证，不能是万能恭维
- **必须来自实际研究** — 看过他们的网站、社交媒体、新闻

```
好：
"Noticed you just expanded into Europe with 3 new warehouse locations."
"Your TikTok content drives massive engagement — 2M views on that last campaign."

坏：
"I came across your brand and was impressed."（太泛，适用于任何人）
"I love what you're doing!"（空洞恭维）
```

**第 2 句：问题诊断（点破他们的结构性瓶颈）**
- 不说 "I'd guess"——你在陈述一个行业事实
- 用 "usually becomes the bottleneck" / "doesn't scale" 这类判断句式
- 让对方感觉 "你说的对，这确实是个问题"
- **诊断角度必须跟用户的产品解决的问题直接相关**

```
好：
"At that scale, coordinating inventory across locations usually becomes the bottleneck."
"But that social engagement rarely converts into repeat purchases — the gap between content and retention is real."

坏：
"I'd guess managing inventory isn't easy"（太猜测、太客气）
"You must be struggling with..."（太假设、太居高临下）
```

**第 3 句：解法（一句话，只留最锋利的一个点）**
- **砍掉一切细节**：不提具体数字承诺、不罗列功能
- 留一个核心锚点：你解决什么 + 怎么解决
- 用 "lightweight" / "no manual work" / "plug-and-play" 降低感知风险

```
好：
"We built a lightweight tool that syncs inventory across all your locations in real-time — no manual reconciliation."

坏：
"We built a platform that provides real-time multi-location inventory synchronization with AI-powered demand forecasting, automated reorder points, and comprehensive analytics dashboard."（功能列表，像产品文档）
```

**第 4 句：免费 offer（包装成 "找反馈"，不是 "促销"）**
- 降低门槛——但包装成合作关系，不是推销
- 强调"我们在找反馈"而不是"我们在找客户"

```
好：
"Happy to set it up free on your end — no commitment, mainly looking for feedback."
"We're onboarding a small group this month — just want the feedback."

坏：
"FREE SETUP! Limited time offer!"（像垃圾邮件）
"We're offering a free trial to selected brands"（像群发促销）
```

**第 5 句：CTA（极轻，允许拒绝）**
- 不要求对方做重的事
- 明确允许对方说不——降低回复心理门槛
- 最好的 CTA 是：对方只需要回复一个词就能推进

```
好：
"If the timing's off, no worries at all."
"Totally fine if it's not the right time."

坏：
"Would you be open to a 30-min call?"（太重）
"Let me know your thoughts!"（太模糊，不知道回什么）
```

### 签名
简洁：
```
— {发件人名}, {公司名}
```
不需要公司介绍、title、电话号码、LinkedIn 链接。冷邮件签名越短越像个人邮件。

## 个性化策略：深度研究 + 定制化

**每封邮件都必须深度个性化。** 不用模板批量生成，而是为每个收件人单独研究、单独撰写。

### 写邮件前必做的研究
对每个收件人，至少完成以下一项：
1. **浏览他们的网站** — 找到具体的产品、页面、功能细节
2. **看他们的社交媒体** — 最近发了什么、粉丝量、互动情况
3. **搜索最近动态** — 新融资、新品线、扩张、合作、新闻
4. **看他们的具体痛点** — 网站哪里可以改进、用户评价说了什么

### 如何用研究成果写邮件
- **第 1 句**直接引用你的发现（具体产品名、具体数据、具体事件）
- **第 2 句**根据这个发现推导出他们可能的瓶颈
- 不是套公式，而是**真的在对话**

### 示例：研究 → 邮件的思路

```
研究发现：这个品牌刚上线了一个新的 B2B wholesale portal，但结账流程还是手动发 invoice
→ 观察："Noticed you just launched your wholesale portal — great move."
→ 诊断："But the manual invoicing step usually kills conversion at scale — buyers expect checkout to be instant."
→ 解法：一句话说你怎么解决这个
```

```
研究发现：这个 DTC 品牌 IG 粉丝 500K，但网站 review 只有 200 条
→ 观察："Your IG following is massive — 500K and growing."
→ 诊断："But that engagement rarely translates to on-site social proof — most brands in your position have a review gap."
→ 解法：一句话
```

## 批量生成策略

即使是 50 封邮件，每封也要有独特的观察和诊断。但可以用以下方式提高效率：

### 第 1 步：按收件人的"可诊断维度"分组
根据用户的产品，识别收件人可能存在的不同瓶颈。例如：
- 如果卖 CRM → 按公司规模分（10 人 vs 100 人 vs 1000 人痛点不同）
- 如果卖物流方案 → 按渠道分（纯线上 vs 有线下 vs 跨境痛点不同）
- 如果卖营销工具 → 按现有工具栈分（用 Mailchimp 的 vs 用 HubSpot 的痛点不同）

### 第 2 步：每组共享"诊断角度"，但每封的"观察句"必须独特
- 同一组的问题诊断可以用类似的切入角度
- 但第 1 句的观察必须来自对该品牌的具体研究
- 标题从公式池里轮换，避免重复

### 第 3 步：标题和 CTA 全局去重
- 50 封邮件 50 个不同的标题
- CTA 交替使用不同的轻量句式

## 自检清单

写完每封邮件后，用以下 checklist 自检：
- [ ] 标题像不像同事发来的？（像 → ✅，像广告 → 重写）
- [ ] 删掉产品名和公司名后，邮件还有没有价值？（有 → ✅）
- [ ] 第一句是关于对方还是关于你？（对方 → ✅）
- [ ] 第一句是否来自真实研究，而不是泛泛恭维？（具体 → ✅）
- [ ] 问题诊断句是陈述事实还是在猜测？（事实 → ✅，"I'd guess" → 重写）
- [ ] 产品介绍超过一句话了吗？（一句 → ✅，多句 → 砍）
- [ ] 有没有具体数字承诺？（没有 → ✅，有 → 删除）
- [ ] CTA 是否允许对方说不？（是 → ✅）
- [ ] 正文总词数 < 100？（是 → ✅）

## 注意事项

- **每封邮件必须像人写的**，不像 AI 生成的模板
- **长度上限 100 词正文**（不含签名），超了必须砍
- **不要用 bold、bullet points、formatting**——纯文本，像个人邮件
- **不要在第一封邮件推 demo/call**——先建联，后面跟进时再推
- **标题不要超过 7 个词**
- **不要承诺具体 ROI 数字**——早期产品用"结构性改善"而不是"数字承诺"
- **如果用户提供了模板**，在模板基础上优化，但仍然遵循以上原则
- **不需要退订提示**——冷邮件用轻量 CTA 中的 "no worries" 已经足够人性化
