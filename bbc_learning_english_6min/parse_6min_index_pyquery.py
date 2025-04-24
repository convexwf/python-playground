# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : bbc_learning_english_6min/parse_6min_index_pyquery.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-24 22:15
# @UpdateTime : 2025-04-24 22:15
"""Parse BBC Learning English 6 Minute English index HTML and extract episode URLs.

Why:
- The directory page lists episodes; we want the per-episode page URLs (where transcript lives).

Usage:
  python tools/parse_6min_index_pyquery.py ./data/bbc_6min_index.html
  python tools/parse_6min_index_pyquery.py ./data/bbc_6min_index.html -o ./data/bbc_6min_episode_urls.txt

Output:
- One absolute URL per line.
"""

import argparse
import re
from pathlib import Path
from typing import List, Set

from pyquery import PyQuery as pq

BBC_BASE = "https://www.bbc.co.uk"


def _is_episode_path(href: str) -> bool:
    # Examples:
    # /learningenglish/english/features/6-minute-english_2026/260122
    # /learningenglish/english/features/6-minute-english_2026/ep-260115
    # /learningenglish/english/features/6-minute-english/ep-160915
    if not href:
        return False
    if not href.startswith("/learningenglish/english/features/6-minute-english"):
        return False
    return bool(re.search(r"/6-minute-english(?:_\d{4})?/(ep-)?\d{6}$", href))


def extract_episode_urls(
    doc: pq,
    *,
    base_url: str = BBC_BASE,
    relative: bool = False,
    limit: int = 0,
) -> List[str]:
    urls: List[str] = []
    seen: Set[str] = set()

    for a in doc("a[href]").items():
        href = (a.attr("href") or "").strip()
        if not _is_episode_path(href):
            continue
        url = href if relative else (base_url.rstrip("/") + href)
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)

        if limit > 0 and len(urls) >= limit:
            break

    return urls


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Extract 6 Minute English episode URLs from index HTML (pyquery)"
    )
    ap.add_argument("html", help="Local HTML file path")
    ap.add_argument("-o", "--output", help="Output file path; default: stdout")
    ap.add_argument(
        "--base-url",
        default=BBC_BASE,
        help=f"Base URL for absolute output (default: {BBC_BASE})",
    )
    ap.add_argument(
        "--relative",
        action="store_true",
        help="Output relative paths (start with /...) instead of absolute URLs",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only output first N URLs (default: 0 = no limit)",
    )
    args = ap.parse_args()

    html = Path(args.html).read_text(encoding="utf-8", errors="ignore")
    doc = pq(html)

    urls = extract_episode_urls(
        doc,
        base_url=args.base_url,
        relative=args.relative,
        limit=args.limit,
    )
    if not urls:
        raise SystemExit("未在目录页中找到 episode 链接（选择器/规则可能需要调整）。")

    text = "\n".join(urls) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Saved -> {out}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
