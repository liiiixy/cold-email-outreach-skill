# Skill: Skill 发布器 (Skill Publisher)

## 触发条件
当用户提到以下意图时激活：

- "发布 skill"、"publish skill"、"推送到 GitHub"、"push to GitHub"
- "把这个 skill 分享给别人"
- "发布到 GitHub"

## 概述

将已构建好的 Skill 项目推送到 GitHub 仓库，让其他人可以 `git clone` 安装使用。

**本 skill 只负责发布到 GitHub**——Skill 的生成和打包由 `skill-builder.md` 完成。如果项目还没有构建（缺少 README / install.sh / .gitignore），提示用户先运行 `/skill_builder`。

---

## 第 1 步：检查项目就绪状态

确认以下文件存在：

```
必须有：
✅ .claude/skills/*.md — 至少一个 Skill 文件
✅ README.md

推荐有：
⚠️ install.sh — 一键安装脚本
⚠️ .gitignore — 排除敏感文件
```

如果缺少必要文件：
> "项目还没有打包完成，缺少 README.md。建议先运行 `/skill_builder` 构建项目，然后再发布。要先构建吗？"

## 第 2 步：发布前安全检查（强制）

扫描所有待推送文件，检查敏感信息：

- 邮箱密码 / App Password
- API Key（`SG.` / `re_` / `sk_` / `ghp_` 开头）
- 硬编码邮箱地址
- 绝对路径（`/Users/xxx/...`、`/home/xxx/...`）
- IP 地址
- token / secret / credential 赋值

发现问题必须处理后才能继续。

## 第 3 步：确认推送信息

> "即将推送到 GitHub：
> - 仓库名：`<仓库名>`
> - 可见性：`public`
> - 文件数：`X 个`
> - 包含的 Skill：[列表]
>
> 确认推送？"

**等待用户确认后才能推送。**

## 第 4 步：推送到 GitHub

**优先用 GitHub CLI（`gh`）**：

```bash
# 检查是否已安装和登录
gh auth status

# 创建仓库并推送（如果仓库不存在）
gh repo create <仓库名> --public --source=. --push

# 如果仓库已存在
git add . && git commit -m "Update skills" && git push origin main
```

**备选：GitHub MCP**：
```
mcp__github__create_repository → mcp__github__push_files
```

**备选：手动 git**：
```bash
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

## 第 5 步：推送后验证

> "✅ 发布成功！
>
> 🔗 仓库地址：https://github.com/<用户名>/<仓库名>
>
> 别人安装方式：
> ```
> git clone https://github.com/<用户名>/<仓库名>.git
> cd <仓库名>
> ./install.sh /path/to/project
> ```"

---

## 注意事项

- **绝对不能推送包含密码、token、个人邮箱的文件**
- 安全检查是强制步骤，不能跳过
- 如果 GitHub 认证失败，给出所有可用的认证方式让用户选择
- 仓库默认 public（用户可以改为 private）
- 每次推送生成新的 commit，不覆盖历史
