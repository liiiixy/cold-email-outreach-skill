---
name: skill_builder
description: 从对话中生成 Skill 并打包，可选发布到 GitHub
---

帮我把刚才完成的任务打包成一个可复用的 Claude Code Skill。

请严格按照 `.claude/skills/skill-builder.md` 中定义的工作流程执行：
1. 分析对话，提炼流程
2. 设计 Skill 架构
3. 生成 Skill .md 文件
4. 处理配套代码
5. 用户审核
6. 安全检查
7. 生成 README / install.sh / .gitignore
8. 生成斜杠命令

构建完成后，询问用户是否需要继续发布到 GitHub（调用 `.claude/skills/skill-publisher.md`）。

如果用户提供了额外参数：$ARGUMENTS
