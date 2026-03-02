# Cold Email Outreach Skill for Claude Code

一套运行在 [Claude Code](https://claude.ai/claude-code) 中的冷邮件自动化 Skill。从找到目标客户到个性化邮件发送、追踪，全流程自动化。

适用于任何产品/服务的冷启动邮件建联，不限行业。

## 它能做什么

| 步骤 | Skill | 说明 |
|------|-------|------|
| 1 | lead-researcher | 研究并筛选目标客户（支持 Excel/URL/文字描述等任意输入） |
| 2 | email-finder | 多层策略查找联系邮箱（WebSearch → WebFetch → 浏览器） |
| 3 | email-copywriter | 逐个研究收件人，撰写高回复率个性化冷邮件 |
| 4 | email-sender | 批量发送 + 退信检测 + 自动重发 + 追踪报告 |
| 5 | email-followup | 智能分类回复（真人/自动）+ 意图分析 + 针对性跟进 |

## 架构

```
outreach-campaign（编排器）
    ├── 第1步 → lead-researcher（找目标客户）
    ├── 第2步 → email-finder（找邮箱）
    ├── 第3步 → email-copywriter（写邮件）
    ├── 第4步 → email-sender（发送+追踪）
    └── 第5步 → email-followup（智能跟进）
```

6 个 Skill 各自独立、各自可触发，也可通过主流程串联。

## 安装

### 前提条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 已安装
- Python 3.9+
- Gmail 账号 + App Password（用于发送邮件）

### 一键安装

```bash
git clone https://github.com/YOUR_USERNAME/cold-email-outreach-skill.git
cd cold-email-outreach-skill
chmod +x install.sh
./install.sh
```

安装脚本会：
1. 将 6 个 Skill 文件复制到 `.claude/skills/` 目录
2. 将 Python 模块复制到 `scripts/outreach/` 目录
3. 安装 Python 依赖

### 手动安装

```bash
# 1. 复制 skill 文件
mkdir -p YOUR_PROJECT/.claude/skills
cp .claude/skills/*.md YOUR_PROJECT/.claude/skills/

# 2. 复制 Python 模块
mkdir -p YOUR_PROJECT/scripts/outreach
cp scripts/outreach/*.py YOUR_PROJECT/scripts/outreach/
cp scripts/outreach/requirements.txt YOUR_PROJECT/scripts/outreach/

# 3. 安装依赖
pip3 install -r YOUR_PROJECT/scripts/outreach/requirements.txt
```

## 使用方法

在项目目录下启动 Claude Code，用自然语言触发：

### 完整流程

```
帮我做一轮冷邮件 outreach
```

Claude 会自动进入 5 步流程，逐步引导你完成。

### 单独使用某个能力

| 说这句话 | 触发的 Skill |
|---------|------------|
| "帮我找 50 个适合我产品的 DTC 品牌" | lead-researcher |
| "找 Allbirds 的联系邮箱" | email-finder |
| "帮我写一封给 Nike 的冷邮件" | email-copywriter |
| "帮我把这些邮件发出去" | email-sender |
| "检查上次发的邮件有没有退信" | email-sender |
| "帮我看一下昨天发的邮件有没有人回" | email-followup |
| "给没回复的人发 follow-up" | email-followup |

### 支持的客户来源

不限于 Excel 表格——你可以用任何形式告诉 Claude 你想联系谁：

| 输入形式 | 示例 |
|---------|------|
| Excel/CSV 文件 | "这是我的商家列表 merchants.xlsx" |
| URL 列表 | "帮我看看这 20 个网站" |
| 品牌名 | "我想联系 Allbirds, Everlane, Warby Parker" |
| 文字描述 | "帮我找 50 个做 DTC 护肤品的品牌" |

## 配置 Gmail 发送

1. 开启 Gmail 两步验证
2. 生成 App Password：[Google 安全设置](https://myaccount.google.com/apppasswords)
3. 运行完整流程时，系统会在发送步骤要求你输入凭据

> 凭据不会被保存到文件，仅在当次会话中使用。

## 冷邮件写作理念

- **问题诊断 > 产品介绍**：点破对方正在承受的问题，而不是介绍你的产品
- **深度个性化**：每封邮件都基于对收件人的实际研究（网站、社交、新闻）
- **极简**：正文不超过 100 词，4-5 句话
- **低门槛 CTA**：允许对方说不，降低回复心理门槛
- **不像 AI**：纯文本，像一个真人同事发的邮件

## 项目结构

```
your-project/
├── .claude/
│   └── skills/
│       ├── outreach-campaign.md    # 主流程编排器
│       ├── lead-researcher.md      # 目标客户研究与筛选
│       ├── email-finder.md         # 邮箱查找
│       ├── email-copywriter.md     # 冷邮件撰写
│       ├── email-sender.md         # 发送与追踪
│       └── email-followup.md      # 智能跟进
├── scripts/
│   └── outreach/
│       ├── input_parser.py         # 文件解析（通用）
│       ├── lead_scorer.py          # 客户评分（通用）
│       ├── email_finder.py         # 邮箱提取
│       ├── email_generator.py      # 邮件生成（通用）
│       ├── email_sender.py         # SMTP 发送
│       ├── inbox_scanner.py        # 收件箱扫描
│       ├── reporter.py             # 报告生成
│       └── requirements.txt        # Python 依赖
```

## FAQ

**Q: 需要 API Key 吗？**
A: 不需要额外的 API Key。Skill 使用 Claude Code 本身的能力，加上 Gmail SMTP 发送邮件。

**Q: 一次能发多少封？**
A: 建议每次不超过 50 封，邮件之间有 30-60 秒间隔，避免被 Gmail 限速。

**Q: 数据安全？**
A: 所有数据都在本地处理，不上传到任何第三方服务。

## License

MIT
