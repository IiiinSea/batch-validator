#!/usr/bin/env python3
"""
Smart stats fetching using Claude to analyze web pages
This script fetches HTML and saves it for Claude to analyze
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse


def fetch_and_save_html(url, output_dir):
    """Fetch HTML and save to file for Claude analysis"""
    try:
        import requests
        from bs4 import BeautifulSoup

        print(f"Fetching: {url}")

        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        response.raise_for_status()

        # Parse and clean HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style tags
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()

        # Get text content
        text_content = soup.get_text(separator='\n', strip=True)

        # Save to file
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from URL
        domain = urlparse(url).netloc.replace('.', '_')
        path = urlparse(url).path.replace('/', '_')[:50]
        filename = f"{domain}{path}.txt"

        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n")
            f.write("=" * 80 + "\n\n")
            f.write(text_content)

        print(f"✓ Saved to: {output_path}")
        print(f"  Size: {len(text_content)} characters")

        return {
            'url': url,
            'file': str(output_path),
            'success': True,
            'text_length': len(text_content)
        }

    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            'url': url,
            'error': str(e),
            'success': False
        }


def extract_stats_from_text(text_file):
    """
    Placeholder for Claude to analyze the text file
    In practice, Claude would read this file and extract stats
    """
    print(f"\nTo extract stats from {text_file}:")
    print("1. Use Claude's Read tool to view the file")
    print("2. Ask Claude to find:")
    print("   - 粉丝数 / follower count")
    print("   - 阅读量 / view count")
    print("   - 发布账号 / author")
    print("3. Claude will extract these using its understanding")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 fetch_stats_smart.py <output_dir> <url1> [url2] ...")
        print("\nExample:")
        print("  python3 fetch_stats_smart.py ./web_content https://example.com/article1")
        sys.exit(1)

    # Check dependencies
    try:
        import requests
        import bs4
    except ImportError:
        print("Error: Missing dependencies. Install with:")
        print("  pip install requests beautifulsoup4")
        sys.exit(1)

    output_dir = sys.argv[1]
    urls = sys.argv[2:]

    print(f"Fetching {len(urls)} URLs...")
    print("=" * 80)

    results = []
    for url in urls:
        result = fetch_and_save_html(url, output_dir)
        results.append(result)
        print()

    # Summary
    print("=" * 80)
    print("Summary:")
    print(f"  Total: {len(results)}")
    print(f"  Success: {sum(1 for r in results if r['success'])}")
    print(f"  Failed: {sum(1 for r in results if not r['success'])}")

    # Save results manifest
    manifest_path = Path(output_dir) / "fetch_results.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to: {manifest_path}")
    print("\nNext step: Use Claude to analyze the saved HTML files")
    print("  Example: Read each .txt file and extract follower/view counts")
