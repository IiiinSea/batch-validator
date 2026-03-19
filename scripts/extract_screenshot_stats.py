#!/usr/bin/env python3
"""
Helper script to extract stats from screenshots
Generates a task list for Claude to process
"""

import sys
import json
from pathlib import Path


def create_extraction_tasks(slides_dir, ppt_text_json, output_json):
    """
    Create a task list for extracting stats from screenshots

    Args:
        slides_dir: Directory containing slide images
        ppt_text_json: JSON file with PPT text data (contains URLs)
        output_json: Output file for task list
    """
    slides_dir = Path(slides_dir)

    # Load PPT text data to get URLs
    with open(ppt_text_json, 'r', encoding='utf-8') as f:
        ppt_data = json.load(f)

    # Find slide images
    slide_images = sorted(slides_dir.glob("slide_*.png"))

    tasks = []

    for img_path in slide_images:
        # Extract slide number from filename
        slide_num = int(img_path.stem.split('_')[1])
        slide_key = f"slide_{slide_num:03d}"

        # Get corresponding URL from PPT data
        slide_info = ppt_data.get(slide_key, {})
        url = None

        # Extract URL from text
        text_lines = slide_info.get('text_lines', [])
        for line in text_lines:
            if '见刊链接' in line or 'http' in line:
                # Extract URL
                import re
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    url = url_match.group(0)
                    break

        task = {
            'slide_number': slide_num,
            'image_path': str(img_path),
            'url': url,
            'followers': None,
            'views': None,
            'status': 'pending'
        }

        tasks.append(task)

    # Save tasks
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    print(f"✓ Created {len(tasks)} extraction tasks")
    print(f"✓ Task list saved to: {output_json}")
    print()
    print("Next steps:")
    print("1. Claude will read each slide image")
    print("2. Extract follower count and view count")
    print("3. Update the JSON file with extracted data")
    print(f"4. Use the updated JSON in validation")

    return tasks


def display_extraction_template(task):
    """Display template for extracting stats from one slide"""
    print(f"\n{'='*80}")
    print(f"Slide {task['slide_number']}")
    print(f"{'='*80}")
    print(f"Image: {task['image_path']}")
    print(f"URL:   {task['url']}")
    print()
    print("Claude, please:")
    print(f"1. Read the image: {task['image_path']}")
    print("2. Find and extract:")
    print("   - 粉丝数/粉丝量 (follower count)")
    print("   - 阅读量/浏览量 (view count)")
    print("3. Update this task with:")
    print(f'   "followers": "<number>",')
    print(f'   "views": "<number>",')
    print(f'   "status": "completed"')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 extract_screenshot_stats.py <slides_dir> <ppt_text.json> <output.json>")
        print()
        print("Example:")
        print("  python3 extract_screenshot_stats.py ./slides ./ppt_text.json ./screenshot_stats.json")
        sys.exit(1)

    slides_dir = sys.argv[1]
    ppt_text_json = sys.argv[2]
    output_json = sys.argv[3]

    tasks = create_extraction_tasks(slides_dir, ppt_text_json, output_json)

    # Display first task as example
    if tasks:
        print("\n" + "="*80)
        print("Example: First task")
        print("="*80)
        display_extraction_template(tasks[0])
