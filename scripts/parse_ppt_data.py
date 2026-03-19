#!/usr/bin/env python3
"""
Parse PPT text data to extract structured information
"""

import json
import re
from pathlib import Path


def parse_slide_text(text_lines):
    """
    Parse slide text to extract structured data

    Expected format:
    媒体平台：xxx
    见刊账号：xxx
    见刊日期：xxx
    见刊位置：xxx
    见刊标题：xxx
    见刊链接：xxx
    """
    data = {}

    # Join all lines into one text block
    full_text = "\n".join(text_lines) if isinstance(text_lines, list) else text_lines

    # Extract fields using regex
    # Handle both \n and \x0b as separators
    patterns = {
        'platform': r'媒体平台[：:]\s*([^\n\x0b]+)',
        'account': r'见刊账号[：:]\s*([^\n\x0b]+)',
        'date': r'见刊日期[：:]\s*([^\n\x0b]+)',
        'position': r'见刊位置[：:]\s*([^\n\x0b]+)',
        'title': r'见刊标题[：:]\s*([^\n\x0b]+)',
        'link': r'见刊链接[：:]\s*(.+?)(?=\s*$)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            data[key] = match.group(1).strip()

    return data


def load_ppt_text_data(json_path):
    """Load PPT text data from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_all_slides(json_path):
    """Parse all slides from JSON file"""
    ppt_data = load_ppt_text_data(json_path)

    parsed_data = []

    for slide_key in sorted(ppt_data.keys()):
        slide_info = ppt_data[slide_key]
        slide_num = slide_info['slide_number']
        text_lines = slide_info.get('text_lines', [])

        parsed = parse_slide_text(text_lines)
        parsed['slide_number'] = slide_num

        parsed_data.append(parsed)

    return parsed_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 parse_ppt_data.py <ppt_text.json>")
        sys.exit(1)

    json_file = sys.argv[1]

    print("Parsing PPT text data...")
    print("=" * 80)

    parsed = parse_all_slides(json_file)

    for data in parsed:
        print(f"\nSlide {data['slide_number']}:")
        print(f"  平台: {data.get('platform', 'N/A')}")
        print(f"  标题: {data.get('title', 'N/A')[:50]}...")
        print(f"  日期: {data.get('date', 'N/A')}")
        print(f"  位置: {data.get('position', 'N/A')}")
        print(f"  账号: {data.get('account', 'N/A')}")

    print("\n" + "=" * 80)
    print(f"✓ Parsed {len(parsed)} slides")
