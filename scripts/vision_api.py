#!/usr/bin/env python3
"""
Vision API abstraction layer - supports multiple LLM platforms
Supports: Claude (Anthropic), GPT-4V (OpenAI), Gemini (Google)
"""

import base64
import os
from pathlib import Path
import json


def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def extract_stats_claude(image_path, api_key=None):
    """Extract stats using Claude (Anthropic)"""
    try:
        from anthropic import Anthropic

        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {'error': 'ANTHROPIC_API_KEY not set'}

        client = Anthropic(api_key=api_key)

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Get image extension
        ext = Path(image_path).suffix[1:]  # .png -> png

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": f"image/{ext}",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": """请从这张截图中提取以下信息（如果有的话）：
1. 粉丝数/粉丝量/关注数
2. 阅读量/浏览量/观看数

请以JSON格式返回：
{"followers": "数字或null", "views": "数字或null"}

只返回数字，不要单位。如果找不到则返回null。"""
                        }
                    ],
                }
            ],
        )

        # Parse response
        response_text = message.content[0].text
        result = json.loads(response_text)

        return {
            'followers': result.get('followers'),
            'views': result.get('views'),
            'backend': 'claude'
        }

    except ImportError:
        return {'error': 'anthropic package not installed. Install with: pip install anthropic'}
    except Exception as e:
        return {'error': f'Claude API error: {str(e)}'}


def extract_stats_openai(image_path, api_key=None):
    """Extract stats using GPT-4V (OpenAI)"""
    try:
        from openai import OpenAI

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {'error': 'OPENAI_API_KEY not set'}

        client = OpenAI(api_key=api_key)

        # Encode image
        base64_image = encode_image(image_path)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请从这张截图中提取以下信息（如果有的话）：
1. 粉丝数/粉丝量/关注数
2. 阅读量/浏览量/观看数

请以JSON格式返回：
{"followers": "数字或null", "views": "数字或null"}

只返回数字，不要单位。如果找不到则返回null。"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=300,
        )

        result = json.loads(response.choices[0].message.content)

        return {
            'followers': result.get('followers'),
            'views': result.get('views'),
            'backend': 'openai'
        }

    except ImportError:
        return {'error': 'openai package not installed. Install with: pip install openai'}
    except Exception as e:
        return {'error': f'OpenAI API error: {str(e)}'}


def extract_stats_gemini(image_path, api_key=None):
    """Extract stats using Gemini (Google)"""
    try:
        import google.generativeai as genai
        from PIL import Image

        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {'error': 'GOOGLE_API_KEY not set'}

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-1.5-pro')

        img = Image.open(image_path)

        prompt = """请从这张截图中提取以下信息（如果有的话）：
1. 粉丝数/粉丝量/关注数
2. 阅读量/浏览量/观看数

请以JSON格式返回：
{"followers": "数字或null", "views": "数字或null"}

只返回数字，不要单位。如果找不到则返回null。"""

        response = model.generate_content([prompt, img])
        result = json.loads(response.text)

        return {
            'followers': result.get('followers'),
            'views': result.get('views'),
            'backend': 'gemini'
        }

    except ImportError:
        return {'error': 'google-generativeai package not installed. Install with: pip install google-generativeai'}
    except Exception as e:
        return {'error': f'Gemini API error: {str(e)}'}


def auto_extract_stats(image_path, preferred_backend=None):
    """
    Automatically extract stats using available vision API

    Args:
        image_path: Path to the screenshot
        preferred_backend: 'claude', 'openai', 'gemini', or None (auto-detect)

    Returns:
        dict with followers, views, and backend info
    """
    # Try backends in order of preference
    backends = []

    if preferred_backend:
        backends = [preferred_backend]
    else:
        # Auto-detect based on available API keys
        if os.getenv("ANTHROPIC_API_KEY"):
            backends.append('claude')
        if os.getenv("OPENAI_API_KEY"):
            backends.append('openai')
        if os.getenv("GOOGLE_API_KEY"):
            backends.append('gemini')

    if not backends:
        return {
            'error': 'No vision API configured. Set one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY'
        }

    # Try each backend
    for backend in backends:
        print(f"  [Vision API] 使用 {backend.upper()} 识别截图...")

        if backend == 'claude':
            stats = extract_stats_claude(image_path)
        elif backend == 'openai':
            stats = extract_stats_openai(image_path)
        elif backend == 'gemini':
            stats = extract_stats_gemini(image_path)
        else:
            continue

        if 'error' not in stats:
            return stats
        else:
            print(f"    ⚠ {backend} 失败: {stats['error']}")

    return {'error': 'All vision API backends failed'}


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 vision_api.py <image_path>")
        print()
        print("Extract follower count and view count from screenshot using Vision API")
        print()
        print("Supported backends (auto-detected via API keys):")
        print("  - Claude (Anthropic): set ANTHROPIC_API_KEY")
        print("  - GPT-4V (OpenAI): set OPENAI_API_KEY")
        print("  - Gemini (Google): set GOOGLE_API_KEY")
        print()
        print("Example:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        print("  python3 vision_api.py slide_001.png")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"Analyzing image: {image_path}")
    print("=" * 80)

    stats = auto_extract_stats(image_path)

    print("\nResults:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
