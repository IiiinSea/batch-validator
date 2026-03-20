#!/usr/bin/env python3
"""
Kimi K2.5 图片内容提取器 —— 从图片中提取用户指定字段，返回 JSON。

用法:
  uv run scripts/extract_content.py \
      --images img1.png img2.png \
      --fields "平台名称" "文章标题" "粉丝数"

  uv run scripts/extract_content.py \
      --images img1.png \
      --schema schema.json \
      --output result.json
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path

from openai import OpenAI

API_BASE = "https://api.moonshot.cn/v1"
DEFAULT_MODEL = "kimi-k2.5"


# ── System Prompt 构建 ──────────────────────────────────────────────

def build_system_prompt(fields: list[dict]) -> str:
    field_desc = "\n".join(
        f'  - "{f["name"]}"{_field_hint(f)}'
        for f in fields
    )
    return f"""\
你是一个专业的图片内容提取器。你的唯一任务是：从用户提供的图片中，精准识别并提取指定字段的信息。

## 提取字段

{field_desc}

## 输出规则

1. 严格输出合法 JSON，不要输出任何其他文字。
2. 如果用户传入 N 张图片，返回一个长度为 N 的 JSON 数组，每个元素对应一张图片（按传入顺序）。
3. 如果只有 1 张图片，也返回数组（长度为 1）。
4. 每个元素是一个对象，key 就是上面列出的字段名。
5. 如果某个字段在图片中找不到，对应值填 null —— 绝对不要编造数据。
6. 数字类型的字段，如果图中显示的是带单位的文本（如 "1.2万"），请转换为纯数字（如 12000）。
"""


def _field_hint(f: dict) -> str:
    parts = []
    if desc := f.get("description"):
        parts.append(desc)
    if tp := f.get("type"):
        parts.append(f"类型: {tp}")
    return f"  ({', '.join(parts)})" if parts else ""


# ── 图片编码 ────────────────────────────────────────────────────────

def encode_image(path: str) -> dict:
    mime = mimetypes.guess_type(path)[0] or "image/png"
    data = Path(path).read_bytes()
    url = f"data:{mime};base64,{base64.b64encode(data).decode()}"
    return {"type": "image_url", "image_url": {"url": url}}


# ── 消息组装 ────────────────────────────────────────────────────────

def build_messages(
    images: list[str],
    fields: list[dict],
) -> list[dict]:
    system = {"role": "system", "content": build_system_prompt(fields)}

    content: list[dict] = [encode_image(img) for img in images]
    content.append({
        "type": "text",
        "text": f"请从以上 {len(images)} 张图片中提取指定字段，返回 JSON 数组。",
    })

    user = {"role": "user", "content": content}
    return [system, user]


# ── API 调用 ────────────────────────────────────────────────────────

def extract(
    images: list[str],
    fields: list[dict],
    *,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
) -> list[dict]:
    key = api_key or os.environ.get("MOONSHOT_API_KEY") or os.environ.get("MOONSHOT_MODEL_KEY")
    if not key:
        sys.exit("错误: 请设置 MOONSHOT_API_KEY 或 MOONSHOT_MODEL_KEY 环境变量")

    client = OpenAI(api_key=key, base_url=API_BASE)
    messages = build_messages(images, fields)

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )

    raw = resp.choices[0].message.content
    result = json.loads(raw)

    if isinstance(result, dict):
        result = result.get("data") or result.get("results") or [result]
    return result


# ── Schema / Fields 解析 ────────────────────────────────────────────

def load_fields(args) -> list[dict]:
    if args.schema:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
        return schema.get("fields", schema) if isinstance(schema, dict) else schema

    if args.fields:
        return [{"name": f} for f in args.fields]

    sys.exit("错误: 请通过 --fields 或 --schema 指定要提取的字段")


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Kimi K2.5 图片内容提取器",
    )
    parser.add_argument(
        "--images", nargs="+", required=True,
        help="图片文件路径（支持多张）",
    )
    parser.add_argument(
        "--fields", nargs="+",
        help="要提取的字段名列表",
    )
    parser.add_argument(
        "--schema",
        help="字段定义 JSON 文件路径",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"模型名称（默认 {DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出 JSON 文件路径（不指定则打印到终端）",
    )
    args = parser.parse_args()

    for img in args.images:
        if not Path(img).is_file():
            sys.exit(f"错误: 图片文件不存在 — {img}")

    fields = load_fields(args)
    result = extract(args.images, fields, model=args.model)
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"结果已写入 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
