#!/usr/bin/env python3
"""
Extract text content from each PPT slide
"""

import sys
from pathlib import Path
from pptx import Presentation
import json


def extract_text_from_slide(slide):
    """Extract all text from a slide"""
    text_content = []

    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            text_content.append(shape.text.strip())

    return text_content


def extract_ppt_text(ppt_path, output_json=None):
    """
    Extract text from all slides in PPT

    Args:
        ppt_path: Path to the .pptx file
        output_json: Optional path to save JSON output

    Returns:
        Dictionary with slide text content
    """
    prs = Presentation(ppt_path)

    slides_data = {}

    for slide_idx, slide in enumerate(prs.slides, start=1):
        text_content = extract_text_from_slide(slide)

        slides_data[f"slide_{slide_idx:03d}"] = {
            "slide_number": slide_idx,
            "text_lines": text_content,
            "full_text": "\n".join(text_content)
        }

        print(f"Slide {slide_idx}:")
        for line in text_content:
            print(f"  - {line}")
        print()

    # Save to JSON if requested
    if output_json:
        output_path = Path(output_json)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(slides_data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Text content saved to: {output_path}")

    return slides_data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_ppt_text.py <pptx_file> [output_json]")
        sys.exit(1)

    ppt_file = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) >= 3 else None

    print(f"Extracting text from: {ppt_file}\n")
    print("=" * 80)

    slides_data = extract_ppt_text(ppt_file, output_json)

    print("=" * 80)
    print(f"\n✓ Extracted text from {len(slides_data)} slides")
