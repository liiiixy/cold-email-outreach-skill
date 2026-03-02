# Skill: Skill 打包与发布 (Skill Publisher)

## 触发条件
当用户提到以下意图时激活：
- "打包 skill"、"发布 skill"、"publish skill"
- "推送到 GitHub"、"push to GitHub"
- "把这个 skill 分享给别人"、"package this skill"
- "创建 GitHub 仓库并推送"

## 概述
帮助用户将 `.claude/skills/` 中的 Skill 文件 + 配套代码打包成一个可分发的 GitHub 仓库。包含 README、安装脚本、.gitignore，确保没有个人信息泄露。

## 工作流程

### 第 1 步：扫描项目结构

自动识别需要打包的文件：

```
需要打包：
✅ .claude/skills/*.md — Skill 定义文件
✅ scripts/**/*.py — 配套 Python 模块
✅ scripts/**/requirements.txt — Python 依赖
✅ README.md — 如果存在
✅ install.sh — 如果存在
✅ .gitignore — 如果存在
✅ LICENSE — 如果存在

需要排除：
❌ .claude/settings.local.json — 包含个人权限配置
❌ .env / *.env — 环境变量/密码
❌ /tmp/* — 临时运行数据
❌ __pycache__/ — Python 缓存
❌ contact/ — 用户的业务数据
❌ .DS_Store — macOS 系统文件
❌ 任何包含 password/token/key/secret 的文件
```

**展示给用户确认**：
> "以下文件将被打包：
> [文件列表 + 大小]
>
> 以下文件已排除（包含个人信息或非必要）：
> [排除列表]
>
> 确认无误？"

### 第 2 步：安全检查

自动扫描所有待打包文件，检查是否包含敏感信息：

```python
# 检查的模式
敏感模式 = [
    邮箱密码/App Password,
    API Key（以 SG./re_/sk_ 开头的字符串）,
    硬编码的邮箱地址（发件人/测试邮箱）,
    绝对路径（/Users/xxx/...）,
    IP 地址,
    token/secret/credential 相关的赋值语句,
]
```

如果发现敏感信息：
> "⚠️ 发现以下敏感信息，推送前需要处理：
> - `scripts/xxx.py` 第 42 行：包含硬编码邮箱 `user@example.com`
> - `xxx.md` 第 15 行：包含绝对路径 `/Users/username/...`
>
> 我来帮你清理？"

### 第 3 步：生成/更新 README.md

如果项目没有 README.md，自动生成。如果有，检查是否需要更新。

README 应包含：
1. **项目名和一句话描述**
2. **架构图**（Skill 之间的依赖关系）
3. **安装方法**（一键安装 + 手动安装）
4. **使用方法**（触发关键词 + 示例对话）
5. **项目结构**（文件树）
6. **FAQ**

### 第 4 步：生成/更新 install.sh

安装脚本需要：
1. 复制所有 `.claude/skills/*.md` 到目标项目
2. 复制所有 `scripts/` 目录到目标项目
3. 安装 Python 依赖（如果有 requirements.txt）
4. 清晰的安装成功提示 + 使用说明

### 第 5 步：生成 .gitignore

确保排除：
- OS 文件（.DS_Store）
- Python 缓存（__pycache__/）
- 环境变量（.env）
- Claude 本地设置（.claude/settings.local.json）
- 临时数据和用户业务数据

### 第 6 步：初始化 Git + 推送到 GitHub

**方式 1：GitHub MCP（如果可用）**

```
1. mcp__github__create_repository — 创建仓库
2. mcp__github__push_files — 一次推送所有文件
```

**方式 2：GitHub CLI（需要用户安装 gh）**

```bash
# 安装 gh（如果没有）
brew install gh

# 登录
gh auth login

# 创建仓库并推送
gh repo create <仓库名> --public --source=. --push
```

**方式 3：手动 git push（最后手段）**

```bash
# 1. 在 GitHub 网页创建仓库
# 2. 添加 remote
git remote add origin https://github.com/<用户名>/<仓库名>.git
# 3. 推送
git push -u origin main
```

**推送前再次确认**：
> "即将推送到 GitHub：
> - 仓库名：`<仓库名>`
> - 可见性：`public`
> - 文件数：`X 个`
> - 总大小：`XX KB`
>
> 确认推送？"

### 第 7 步：推送后验证

推送成功后：
1. 展示仓库 URL
2. 验证 README 在 GitHub 上正常渲染
3. 给出分享链接和安装指令

> "✅ 推送成功！
>
> 🔗 仓库地址：https://github.com/<用户名>/<仓库名>
>
> 别人安装方式：
> ```
> git clone https://github.com/<用户名>/<仓库名>.git
> cd <仓库名>
> ./install.sh /path/to/project
> ```"

## 独立使用场景

### 场景 1：快速打包当前项目
```
用户："把这个项目打包发到 GitHub"
→ 扫描 → 安全检查 → 生成/更新 README → 推送
```

### 场景 2：只做安全检查
```
用户："检查一下这个项目有没有敏感信息"
→ 只执行第 2 步
```

### 场景 3：生成 README
```
用户："帮我写个 README"
→ 只执行第 3 步
```

## 注意事项

- **绝对不能推送包含密码、token、个人邮箱的文件**
- 推送前的安全检查是强制步骤，不能跳过
- 如果 GitHub 认证失败，给出所有可用的认证方式让用户选择
- 仓库默认设为 public（用户可以改为 private）
- 每次推送都生成新的 commit，不覆盖历史
