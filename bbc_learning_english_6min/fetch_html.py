# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : bbc_learning_english_6min/fetch_html.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-24 22:15
# @UpdateTime : 2025-04-24 22:15
"""
Fetch HTML to a local file using requests, with robots.txt check.
Usage:
  python tools/fetch_html.py "<URL>" -o ./data/page.html
"""
import argparse
import sys
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

import re

import requests

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def can_fetch(url: str, ua: str = UA) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        resp = requests.get(robots_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"robots.txt 获取失败: {e}") from e
    rp = robotparser.RobotFileParser()
    rp.parse(resp.text.splitlines())
    return rp.can_fetch(ua, url)


def main():
    ap = argparse.ArgumentParser(description="Fetch HTML to local file (requests)")
    ap.add_argument("url", help="Target URL to fetch")
    ap.add_argument(
        "-o",
        "--output",
        help="Output HTML file path (default: ./data/<derived>.html)",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout seconds (default: 30)",
    )
    ap.add_argument(
        "--no-robots",
        action="store_true",
        help="Skip robots.txt check (not recommended)",
    )
    args = ap.parse_args()

    if not args.no_robots:
        try:
            allowed = can_fetch(args.url)
        except Exception as e:
            print(
                f"robots.txt 检查失败（{e}）。可重试，或加 --no-robots 跳过检查。",
                file=sys.stderr,
            )
            sys.exit(2)
        if not allowed:
            print("robots.txt 不允许抓取该 URL，已停止。", file=sys.stderr)
            sys.exit(2)

    def _default_output_for(url: str) -> Path:
        parsed = urlparse(url)
        path = (parsed.path or "/").rstrip("/")
        if not path or path == "/":
            stem = "index"
        else:
            stem = path.split("/")[-1] or "index"
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem)
        return Path("data") / f"{stem}.html"

    out_path = Path(args.output) if args.output else _default_output_for(args.url)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.Session() as s:
        r = s.get(args.url, headers=HEADERS, timeout=args.timeout, verify=False)
        r.raise_for_status()
        out_path.write_text(r.text, encoding="utf-8")

    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
