#!/usr/bin/env python3
"""
Fetch follower count and view count from article URLs
Uses requests + beautifulsoup4 to scrape web pages
"""

import sys
import json
import re
from pathlib import Path
from urllib.parse import urlparse


def fetch_yiche_stats(url):
    """Extract stats from Yiche (易车) article"""
    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        stats = {'followers': None, 'views': None}

        # Try to find view count (阅读量)
        # Common patterns: <span class="read">123次阅读</span>
        view_patterns = [
            r'(\d+)次阅读',
            r'阅读[：:]\s*(\d+)',
            r'浏览[：:]\s*(\d+)',
        ]

        text = soup.get_text()
        for pattern in view_patterns:
            match = re.search(pattern, text)
            if match:
                stats['views'] = match.group(1)
                break

        return stats
    except Exception as e:
        return {'error': str(e)}


def fetch_ifeng_stats(url):
    """Extract stats from iFeng (凤凰) article"""
    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        stats = {'followers': None, 'views': None}

        # Parse凤凰新闻 specific structure
        text = soup.get_text()

        # Look for follower count
        follower_match = re.search(r'粉丝[：:]\s*(\d+)', text)
        if follower_match:
            stats['followers'] = follower_match.group(1)

        # Look for view count
        view_match = re.search(r'阅读[：:]\s*(\d+)', text)
        if view_match:
            stats['views'] = view_match.group(1)

        return stats
    except Exception as e:
        return {'error': str(e)}


def fetch_autohome_stats(url):
    """Extract stats from AutoHome (汽车之家) article"""
    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        stats = {'followers': None, 'views': None}

        text = soup.get_text()

        # 汽车之家 patterns
        view_match = re.search(r'(\d+)\s*阅读', text)
        if view_match:
            stats['views'] = view_match.group(1)

        follower_match = re.search(r'(\d+)\s*粉丝', text)
        if follower_match:
            stats['followers'] = follower_match.group(1)

        return stats
    except Exception as e:
        return {'error': str(e)}


def fetch_stats_generic(url):
    """Generic stats extraction for any URL"""
    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        stats = {'followers': None, 'views': None}

        # Generic patterns
        # Followers
        follower_patterns = [
            r'粉丝[数量]?[：:]\s*(\d+)',
            r'(\d+)\s*粉丝',
            r'关注[：:]\s*(\d+)',
        ]

        for pattern in follower_patterns:
            match = re.search(pattern, text)
            if match:
                stats['followers'] = match.group(1)
                break

        # Views
        view_patterns = [
            r'阅读[量]?[：:]\s*(\d+)',
            r'浏览[量]?[：:]\s*(\d+)',
            r'(\d+)\s*阅读',
            r'(\d+)\s*浏览',
            r'点击[：:]\s*(\d+)',
        ]

        for pattern in view_patterns:
            match = re.search(pattern, text)
            if match:
                stats['views'] = match.group(1)
                break

        return stats
    except Exception as e:
        return {'error': str(e)}


def fetch_article_stats(url):
    """
    Fetch follower and view stats from article URL
    Automatically selects the right parser based on domain
    """
    domain = urlparse(url).netloc

    # Select parser based on domain
    if 'yiche.com' in domain:
        return fetch_yiche_stats(url)
    elif 'ifeng.com' in domain:
        return fetch_ifeng_stats(url)
    elif 'autohome.com' in domain:
        return fetch_autohome_stats(url)
    else:
        return fetch_stats_generic(url)


def fetch_all_stats(links):
    """Fetch stats for multiple links"""
    results = {}

    for i, link in enumerate(links, 1):
        print(f"Fetching [{i}/{len(links)}]: {link[:50]}...")
        stats = fetch_article_stats(link)
        results[link] = stats

        if 'error' not in stats:
            print(f"  粉丝: {stats.get('followers', 'N/A')}, 阅读: {stats.get('views', 'N/A')}")
        else:
            print(f"  Error: {stats['error']}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_web_stats.py <url1> [url2] [url3] ...")
        print("   or: python3 fetch_web_stats.py --json <links.json>")
        sys.exit(1)

    # Check dependencies
    try:
        import requests
        import bs4
    except ImportError:
        print("Error: Missing dependencies. Install with:")
        print("  pip install requests beautifulsoup4")
        sys.exit(1)

    if sys.argv[1] == '--json':
        # Load links from JSON file
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            data = json.load(f)
            links = [slide.get('link') for slide in data if slide.get('link')]
    else:
        # Use command line arguments
        links = sys.argv[1:]

    results = fetch_all_stats(links)

    print("\n" + "=" * 80)
    print("Results Summary:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
