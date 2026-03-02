#!/bin/bash
# Cold Email Outreach Skill — 一键安装脚本
# 将 Skill 文件和 Python 模块安装到指定项目目录

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  Cold Email Outreach Skill Installer"
echo "=========================================="
echo ""

# 检查目标目录
if [ "$1" != "" ]; then
    TARGET_DIR="$1"
else
    TARGET_DIR="$(pwd)"
fi

# 如果在源目录内运行，提示需要指定目标
if [ "$TARGET_DIR" = "$SCRIPT_DIR" ]; then
    echo -e "${YELLOW}当前已在 Skill 源目录中。${NC}"
    echo ""
    echo "用法:"
    echo "  ./install.sh /path/to/your/project"
    echo ""
    echo "或者直接在此目录启动 Claude Code 使用。"
    echo ""

    # 直接在当前目录安装依赖
    echo -e "${GREEN}安装 Python 依赖...${NC}"
    pip3 install -r "$SCRIPT_DIR/scripts/outreach/requirements.txt" -q 2>/dev/null || \
    python3 -m pip install -r "$SCRIPT_DIR/scripts/outreach/requirements.txt" -q 2>/dev/null || \
    echo -e "${YELLOW}⚠️  Python 依赖安装失败，请手动运行: pip3 install -r scripts/outreach/requirements.txt${NC}"

    echo ""
    echo -e "${GREEN}✅ 准备就绪！${NC}"
    echo ""
    echo "启动方式："
    echo "  cd $SCRIPT_DIR"
    echo "  claude"
    echo ""
    echo "然后输入："
    echo "  /outreach              — 启动外展流程"
    echo "  /publish               — 打包发布 Skill"
    echo "  或说 \"帮我发一轮冷邮件\""
    exit 0
fi

echo "目标项目: $TARGET_DIR"
echo ""

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ 目标目录不存在: $TARGET_DIR${NC}"
    exit 1
fi

# 复制 Skill 文件
echo -e "${GREEN}[1/4] 复制 Skill 文件...${NC}"
mkdir -p "$TARGET_DIR/.claude/skills"
for skill_file in "$SCRIPT_DIR/.claude/skills/"*.md; do
    cp "$skill_file" "$TARGET_DIR/.claude/skills/"
    echo "  → .claude/skills/$(basename "$skill_file")"
done

# 复制斜杠命令
echo -e "${GREEN}[2/4] 复制斜杠命令...${NC}"
if [ -d "$SCRIPT_DIR/.claude/commands" ]; then
    mkdir -p "$TARGET_DIR/.claude/commands"
    for cmd_file in "$SCRIPT_DIR/.claude/commands/"*.md; do
        cp "$cmd_file" "$TARGET_DIR/.claude/commands/"
        echo "  → .claude/commands/$(basename "$cmd_file") （/$(basename "$cmd_file" .md) 命令）"
    done
fi

# 复制 Python 模块
echo -e "${GREEN}[3/4] 复制 Python 模块...${NC}"
mkdir -p "$TARGET_DIR/scripts/outreach"
cp "$SCRIPT_DIR/scripts/outreach/"*.py "$TARGET_DIR/scripts/outreach/"
cp "$SCRIPT_DIR/scripts/outreach/requirements.txt" "$TARGET_DIR/scripts/outreach/"
echo "  → scripts/outreach/*.py"
echo "  → scripts/outreach/requirements.txt"

# 安装 Python 依赖
echo -e "${GREEN}[4/4] 安装 Python 依赖...${NC}"
pip3 install -r "$TARGET_DIR/scripts/outreach/requirements.txt" -q 2>/dev/null || \
python3 -m pip install -r "$TARGET_DIR/scripts/outreach/requirements.txt" -q 2>/dev/null || \
echo -e "${YELLOW}⚠️  自动安装失败，请手动运行: pip3 install -r $TARGET_DIR/scripts/outreach/requirements.txt${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 安装完成！${NC}"
echo "=========================================="
echo ""
echo "使用方式："
echo "  cd $TARGET_DIR"
echo "  claude"
echo ""
echo "快捷命令："
echo "  /outreach              — 启动外展流程"
echo "  /publish               — 打包发布 Skill"
echo ""
echo "或者对 Claude 说："
echo "  \"帮我发一轮冷邮件\""
echo "  \"help me send outreach emails\""
echo "  \"找邮箱\" / \"写开发信\""
echo ""
