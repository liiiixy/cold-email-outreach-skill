帮我打包和发布 Skill。

请严格按照 `.claude/skills/skill-publisher.md` 中定义的工作流程执行。

根据用户意图判断走哪条路径：
- 如果对话中刚完成了某个任务 → 走「Skill 生成器」流程（G1-G6），从对话中提炼 Skill
- 如果用户要打包已有的 Skill → 走「Skill 发布器」流程（P1-P7），打包推送到 GitHub
- 如果两者都要 → 先生成再发布，一气呵成

如果用户提供了额外参数：$ARGUMENTS
