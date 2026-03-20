#!/bin/bash
# 快速测试脚本

echo "========================================="
echo "Batch Validator 快速测试"
echo "========================================="
echo ""

# 检查测试文件
TEST_DIR="/Users/zhangzhiyong/IdeaProjects/go/mone/jcommon/skills/batch-validator/场景2"
PPT_FILE="$TEST_DIR/夏广州车展新闻稿发稿明细-测试.pptx"
EXCEL_FILE="$TEST_DIR/夏广州车展新闻稿发稿见刊表格-测试.xlsx"

if [ ! -f "$PPT_FILE" ] || [ ! -f "$EXCEL_FILE" ]; then
    echo "❌ 测试文件不存在"
    echo "请将测试文件放到: $TEST_DIR"
    exit 1
fi

echo "✓ 找到测试文件"
echo "  PPT:   $(basename "$PPT_FILE")"
echo "  Excel: $(basename "$EXCEL_FILE")"
echo ""

# 运行校验
echo "开始校验..."
echo ""

cd "$(dirname "$0")/.." || exit 1

uv run scripts/validate.py "$PPT_FILE" "$EXCEL_FILE"

echo ""
echo "========================================="
echo "测试完成！"
echo "请查看生成的校验结果文件"
echo "========================================="
