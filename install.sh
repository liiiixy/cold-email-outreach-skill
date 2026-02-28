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
    echo "然后对 Claude 说："
    echo "  \"帮我发一轮冷邮件\" 或 \"help me send outreach emails\""
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
echo -e "${GREEN}[1/3] 复制 Skill 文件...${NC}"
mkdir -p "$TARGET_DIR/.claude/skills"
cp "$SCRIPT_DIR/.claude/skills/outreach-campaign.md" "$TARGET_DIR/.claude/skills/"
cp "$SCRIPT_DIR/.claude/skills/email-finder.md" "$TARGET_DIR/.claude/skills/"
cp "$SCRIPT_DIR/.claude/skills/email-copywriter.md" "$TARGET_DIR/.claude/skills/"
echo "  → .claude/skills/outreach-campaign.md"
echo "  → .claude/skills/email-finder.md"
echo "  → .claude/skills/email-copywriter.md"

# 复制 Python 模块
echo -e "${GREEN}[2/3] 复制 Python 模块...${NC}"
mkdir -p "$TARGET_DIR/scripts/outreach"
cp "$SCRIPT_DIR/scripts/outreach/"*.py "$TARGET_DIR/scripts/outreach/"
cp "$SCRIPT_DIR/scripts/outreach/requirements.txt" "$TARGET_DIR/scripts/outreach/"
echo "  → scripts/outreach/*.py"
echo "  → scripts/outreach/requirements.txt"

# 安装 Python 依赖
echo -e "${GREEN}[3/3] 安装 Python 依赖...${NC}"
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
echo "然后对 Claude 说："
echo "  \"帮我发一轮冷邮件\""
echo "  \"help me send outreach emails\""
echo "  \"找邮箱\" / \"写开发信\""
echo ""
