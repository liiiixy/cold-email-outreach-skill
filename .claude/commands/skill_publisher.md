---
name: skill_publisher
description: 将已构建的 Skill 项目发布到 GitHub
---

帮我把当前项目中的 Skill 发布到 GitHub。

请严格按照 `.claude/skills/skill-publisher.md` 中定义的工作流程执行：
1. 检查项目就绪状态
2. 安全检查
3. 确认推送信息
4. 推送到 GitHub
5. 验证并给出分享链接

如果项目缺少 README 或 install.sh，提示用户先运行 `/skill_builder` 构建。

如果用户提供了额外参数：$ARGUMENTS
