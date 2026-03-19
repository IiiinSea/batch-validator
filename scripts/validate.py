#!/usr/bin/env python3
"""
主校验脚本 - Excel vs PPT批量校验
这是validate_excel_ppt.py的快捷入口
"""

import sys
from pathlib import Path

# 导入核心校验模块
from validate_excel_ppt import main

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("=" * 80)
        print("Batch Validator - Excel vs PPT 批量校验")
        print("=" * 80)
        print()
        print("用法: uv run scripts/validate.py <ppt文件> <excel文件> [screenshot_stats.json] [输出文件]")
        print()
        print("示例:")
        print("  # 基础校验")
        print("  uv run scripts/validate.py test.pptx test.xlsx")
        print()
        print("  # 完整校验（含截图数据）")
        print("  uv run scripts/validate.py test.pptx test.xlsx screenshot_stats.json")
        print()
        print("3级数据提取优先级：")
        print("  1. PPT文字标注（自动）")
        print("  2. PPT截图识别（需screenshot_stats.json）")
        print("  3. 网页抓取（自动）")
        print()
        sys.exit(1)

    # 调用主函数
    ppt_file = sys.argv[1]
    excel_file = sys.argv[2]
    screenshot_stats_json = sys.argv[3] if len(sys.argv) >= 4 and not sys.argv[3].endswith('.xlsx') else None
    output_file = sys.argv[4] if len(sys.argv) >= 5 else (sys.argv[3] if len(sys.argv) >= 4 and sys.argv[3].endswith('.xlsx') else None)

    main(ppt_file, excel_file, screenshot_stats_json, output_file)
