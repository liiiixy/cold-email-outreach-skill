# Cold Email Outreach Skill for Claude Code

一套运行在 [Claude Code](https://claude.ai/claude-code) 中的冷邮件自动化 Skill。从商家列表到个性化邮件发送、追踪，全流程自动化。

适用于任何产品/服务的冷启动邮件建联，不限行业。

## 它能做什么

| 步骤 | 功能 | 说明 |
|------|------|------|
| 1 | 解析商家列表 | 支持 Excel / CSV / 飞书文档 / 纯文本 |
| 2 | 筛选目标客户 | 根据你的产品定位自动评分排序 |
| 3 | 查找联系邮箱 | 多层策略：WebSearch → WebFetch → 浏览器 |
| 4 | 撰写个性化邮件 | 逐个研究收件人，生成高回复率冷邮件 |
| 5 | 人工审核确认 | 发送前逐封预览，可修改 |
| 6 | 批量发送 | 通过 Gmail SMTP 发送，自动间隔防封 |
| 7 | 追踪退信 | 扫描收件箱，检测退信并尝试修复 |

## 安装

### 前提条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 已安装
- Python 3.9+
- Gmail 账号 + App Password（用于发送邮件）

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/liiiixy1205/cold-email-outreach-skill.git

# 进入目录
cd cold-email-outreach-skill

# 运行安装脚本
chmod +x install.sh
./install.sh
```

安装脚本会：
1. 将 3 个 Skill 文件复制到你当前项目的 `.claude/skills/` 目录
2. 将 Python 模块复制到 `scripts/outreach/` 目录
3. 安装 Python 依赖（openpyxl, requests, beautifulsoup4）

### 手动安装

如果你更喜欢手动操作：

```bash
# 1. 复制 skill 文件到你的项目
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

在你的项目目录下启动 Claude Code，然后用自然语言触发：

### 完整流程（推荐）

直接说：

```
帮我发一轮冷邮件
```

或者：

```
I have a list of merchants, help me send outreach emails
```

Claude 会自动进入完整的 7 步流程，逐步引导你完成。

### 触发关键词

| Skill | 中文触发词 | 英文触发词 |
|-------|-----------|-----------|
| 完整流程 | 发邮件、外展、开发信、批量发送 | outreach, cold email, send emails |
| 只找邮箱 | 找邮箱、找联系方式 | find email, find contact |
| 只写邮件 | 写邮件、写开发信、优化邮件 | write cold email, draft email |

### 使用示例

**场景 1：完整流程**
```
我有一份 Shopify 商家列表（Excel），帮我筛选合适的品牌并发送冷邮件。
我的产品是一个 AI 客服工具，帮 DTC 品牌自动处理退换货。
```

**场景 2：只找邮箱**
```
帮我找 Allbirds 和 Everlane 的联系邮箱
```

**场景 3：只写邮件**
```
帮我写一封给 Nike 的冷邮件，我的产品是 XX，我叫张三，公司叫 YY
```

## 配置 Gmail 发送

1. 开启 Gmail 两步验证
2. 生成 App Password：[Google 安全设置](https://myaccount.google.com/apppasswords)
3. 在 Claude Code 中运行完整流程时，系统会在第 6 步要求你输入：
   - 发件人邮箱
   - App Password
   - 发件人显示名

> 凭据不会被保存到文件，仅在当次会话中使用。

## 项目结构

```
your-project/
├── .claude/
│   └── skills/
│       ├── outreach-campaign.md    # 主流程：7步完整自动化
│       ├── email-finder.md         # 邮箱查找策略
│       └── email-copywriter.md     # 冷邮件撰写原则
├── scripts/
│   └── outreach/
│       ├── input_parser.py         # 文件解析
│       ├── lead_scorer.py          # 客户评分
│       ├── email_finder.py         # 邮箱提取
│       ├── email_generator.py      # 邮件生成
│       ├── email_sender.py         # SMTP 发送
│       ├── inbox_scanner.py        # 收件箱扫描
│       ├── reporter.py             # 报告生成
│       └── requirements.txt        # Python 依赖
```

## Skill 架构

```
outreach-campaign（主流程）
    ├── 第3步 → email-finder（邮箱查找）
    └── 第4步 → email-copywriter（邮件撰写）
```

三个 Skill 可以独立使用，也可以通过主流程串联。

## 冷邮件写作理念

本 Skill 的核心写作原则：

- **问题诊断 > 产品介绍**：点破对方正在承受的问题，而不是介绍你的产品
- **深度个性化**：每封邮件都基于对收件人的实际研究（网站、社交、新闻）
- **极简**：正文不超过 100 词，4-5 句话
- **低门槛 CTA**：允许对方说不，降低回复心理门槛
- **不像 AI**：不用 bold、bullet point，像一个真人同事发的邮件

## FAQ

**Q: 需要 API Key 吗？**
A: 不需要额外的 API Key。Skill 使用 Claude Code 本身的能力，加上 Gmail SMTP 发送邮件。

**Q: 一次能发多少封？**
A: 技术上没有限制，但建议每次不超过 50 封，并且邮件之间有 30-60 秒间隔，避免被 Gmail 限速。

**Q: 支持哪些邮箱？**
A: 发送端目前使用 Gmail SMTP。收件端不限。

**Q: 数据安全？**
A: 所有数据都在你本地处理。商家列表、邮件内容、发送记录都保存在本地 `/tmp/` 目录，不会上传到任何第三方服务。

## License

MIT
