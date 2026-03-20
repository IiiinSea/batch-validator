#!/usr/bin/env python3
"""
PPT 信息智能查询 —— 文字优先，图片兜底。

用法:
  # 查询所有页
  uv run scripts/query_info.py \
    --base "场景2/夏广州车展新闻稿发稿明细-测试" \
    --fields "平台名称" "文章标题" "发布时间" "粉丝数" "阅读量"

  # 只查某一页
  uv run scripts/query_info.py \
    --base "场景2/夏广州车展新闻稿发稿明细-测试" \
    --fields "阅读量" "粉丝数" \
    --slide 7

--base 是 PPT 路径去掉 .pptx 后缀，脚本自动拼接 {base}_text/ 和 {base}_images/。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 复用 extract_content 中的 extract 函数
sys.path.insert(0, str(Path(__file__).parent))
from extract_content import extract as kimi_extract


# ── 文字搜索 ─────────────────────────────────────────────────────────

# 字段名 → 常见 PPT 文字标签映射（宽松匹配）
# key 是用户查询时可能用的字段名，value 是 PPT txt 中对应的标签
_FIELD_ALIASES: dict[str, list[str]] = {
    # 平台
    "平台名称":     ["媒体平台", "发布平台", "平台"],
    "媒体名称":     ["媒体平台", "发布平台", "平台"],
    "媒体名称/平台": ["媒体平台", "发布平台", "平台"],
    # 标题
    "文章标题":     ["见刊标题", "文章标题", "标题"],
    # 时间
    "发布时间":     ["见刊日期", "发布日期", "日期"],
    "发布日期":     ["见刊日期", "发布日期", "日期"],
    # 账号
    "发布账号":     ["见刊账号", "发布账号", "账号"],
    # 位置
    "见刊位置":     ["见刊位置", "刊出位置"],
    "刊出位置":     ["刊出位置", "见刊位置"],
    # 链接
    "见刊链接":     ["见刊链接", "链接"],
    "链接":         ["见刊链接", "链接"],
    # 粉丝（PPT 文字里通常没有，走图片兜底，这里保留方便万一有）
    "粉丝量":       ["粉丝量", "粉丝数", "粉丝"],
    "粉丝数":       ["粉丝数", "粉丝量", "粉丝"],
    # 阅读（PPT 文字里通常没有，走图片兜底）
    "阅读量":       ["阅读量", "阅读"],
}


def _aliases(field: str) -> list[str]:
    return _FIELD_ALIASES.get(field, [field])


def search_in_text(txt_path: Path, fields: list[str]) -> dict[str, str | None]:
    """从单个 slide txt 中提取字段值，返回 {field: value or None}。"""
    text = txt_path.read_text(encoding="utf-8")
    result: dict[str, str | None] = {}

    for field in fields:
        value = None
        for alias in _aliases(field):
            # 匹配 "标签：值" 或 "标签:值"，取到行尾
            m = re.search(rf"{re.escape(alias)}[：:]\s*(.+)", text)
            if m:
                value = m.group(1).strip()
                break
        result[field] = value

    return result


# ── 图片查询（Kimi K2.5）────────────────────────────────────────────

def search_in_images(img_dir: Path, fields: list[str], *, max_retries: int = 3) -> dict[str, object]:
    """对 img_dir 下所有图片调用 Kimi，返回 {field: value or None}。最多重试 max_retries 次。"""
    images = sorted(img_dir.glob("img_*.png"))
    if not images:
        return {f: None for f in fields}

    field_defs = [{"name": f} for f in fields]

    for attempt in range(1, max_retries + 1):
        raw = kimi_extract([str(p) for p in images], field_defs)

        merged: dict[str, object] = {f: None for f in fields}
        for item in raw:
            for field in fields:
                if merged[field] is None and item.get(field) is not None:
                    merged[field] = item[field]

        # 只要有任意字段找到值就认为成功
        if any(v is not None for v in merged.values()):
            return merged

        if attempt < max_retries:
            print(f"    Kimi 返回全 null，第 {attempt} 次重试...")

    return merged


# ── 单页查询 ─────────────────────────────────────────────────────────

def query_slide(
    slide_idx: int,
    txt_dir: Path,
    img_dir: Path,
    fields: list[str],
) -> dict:
    key = f"slide_{slide_idx:03d}"
    txt_path = txt_dir / f"{key}.txt"
    images_dir = img_dir / key

    # Step 1: 文字搜索
    text_result: dict[str, str | None] = {}
    if txt_path.exists():
        text_result = search_in_text(txt_path, fields)

    missing = [f for f in fields if text_result.get(f) is None]

    # Step 2: 图片兜底（仅缺失字段）
    image_result: dict[str, object] = {}
    if missing and images_dir.exists():
        print(f"  slide {slide_idx:03d}: 文字未找到 {missing}，调用 Kimi 查图片...")
        image_result = search_in_images(images_dir, missing)

    # 合并，记录来源
    record: dict = {"slide": slide_idx}
    for field in fields:
        if text_result.get(field) is not None:
            record[field] = {"value": text_result[field], "source": "text"}
        elif image_result.get(field) is not None:
            record[field] = {"value": image_result[field], "source": "image"}
        else:
            record[field] = {"value": None, "source": None}

    return record


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PPT 信息智能查询（文字优先 + Kimi 图片兜底）")
    parser.add_argument("--base", required=True,
                        help="PPT 路径去掉 .pptx，如 '场景2/夏广州车展新闻稿发稿明细-测试'")
    parser.add_argument("--fields", nargs="+", required=True,
                        help="要查询的字段列表")
    parser.add_argument("--slide", type=int, default=None,
                        help="只查指定页（不填则查全部）")
    parser.add_argument("--output", "-o",
                        help="输出 JSON 文件路径（不填则打印到终端）")
    args = parser.parse_args()

    txt_dir = Path(f"{args.base}_text")
    img_dir = Path(f"{args.base}_images")

    if not txt_dir.exists() and not img_dir.exists():
        sys.exit(f"错误: 未找到 {txt_dir} 或 {img_dir}，请先运行「提取信息」步骤")

    # 确定要查哪些页
    if args.slide:
        slide_indices = [args.slide]
    else:
        # 从 txt 或 img 目录推断总页数
        dirs = sorted(img_dir.glob("slide_*")) if img_dir.exists() else []
        txts = sorted(txt_dir.glob("slide_*.txt")) if txt_dir.exists() else []
        keys = {int(p.stem.split("_")[1]) for p in dirs + txts}
        slide_indices = sorted(keys) if keys else []

    if not slide_indices:
        sys.exit("错误: 未找到任何已提取的页面数据")

    results = []
    for idx in slide_indices:
        print(f"查询第 {idx} 页...")
        record = query_slide(idx, txt_dir, img_dir, args.fields)
        results.append(record)

    output = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n结果已写入 {args.output}")
    else:
        print("\n" + output)


if __name__ == "__main__":
    main()
