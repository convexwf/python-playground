# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : bbc_learning_english_6min/batch_fetch_transcripts.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-24 22:15
# @UpdateTime : 2025-04-26 10:29
"""
Batch fetch BBC 6 Minute English episode pages from a URL list
and parse transcripts to Markdown.

Usage:
  python batch_fetch_transcripts.py ./tmp/bbc_6min_episode_urls.txt \
    --html-dir ./tmp/html --md-dir ./tmp/md
"""
import argparse
import re
import sys
import time
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urlparse

import requests
from pyquery import PyQuery as pq

import parse_transcript_pyquery as pt
from fetch_html import HEADERS, can_fetch

BBC_BASE = "https://www.bbc.co.uk"


def _read_urls(path: Path) -> List[str]:
    lines: List[str] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


def _normalize_url(s: str, base_url: str) -> str:
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if s.startswith("/"):
        return base_url.rstrip("/") + s
    return base_url.rstrip("/") + "/" + s.lstrip("/")


def _slug_from_url(url: str) -> str:
    path = (urlparse(url).path or "/").rstrip("/")
    if not path or path == "/":
        stem = "index"
    else:
        stem = path.split("/")[-1] or "index"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem)
    if re.fullmatch(r"\d{6}", stem):
        stem = f"ep-{stem}"
    return stem


def _fetch_html(url: str, out_path: Path, timeout: int, no_robots: bool) -> None:
    if not no_robots:
        try:
            allowed = can_fetch(url)
        except Exception as e:
            print(
                f"robots.txt 检查失败（{e}）。可重试，或加 --no-robots 跳过检查。",
                file=sys.stderr,
            )
            raise
        if not allowed:
            raise RuntimeError("robots.txt 不允许抓取该 URL")

    with requests.Session() as s:
        r = s.get(url, headers=HEADERS, timeout=timeout, verify=False)
        r.raise_for_status()
        out_path.write_text(r.text, encoding="utf-8")


def _parse_to_md(html_path: Path, md_path: Path) -> None:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    doc = pq(html)

    title = pt.extract_title(doc)
    meta = pt.extract_meta(doc)
    sections = pt.collect_sections(doc)

    if not sections:
        raise RuntimeError("未从 HTML 中解析到有效内容")

    md = pt.to_markdown(title, meta, sections)
    md_path.write_text(md, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Batch fetch BBC 6 Minute English pages and parse transcripts"
    )
    ap.add_argument("url_list", help="txt file with one URL per line")
    ap.add_argument(
        "--base-url",
        default=BBC_BASE,
        help=f"Base URL for relative paths (default: {BBC_BASE})",
    )
    ap.add_argument(
        "--html-dir",
        default="./tmp/html",
        help="Directory to save episode HTML (default: ./tmp/html)",
    )
    ap.add_argument(
        "--md-dir",
        default="./tmp/md",
        help="Directory to save transcript Markdown (default: ./tmp/md)",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout seconds (default: 30)",
    )
    ap.add_argument(
        "--sleep",
        type=float,
        default=0.1,
        help="Sleep seconds between requests (default: 0.1)",
    )
    ap.add_argument(
        "--no-robots",
        action="store_true",
        help="Skip robots.txt check (not recommended)",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing HTML/MD files",
    )
    args = ap.parse_args()

    url_list = Path(args.url_list)
    if not url_list.exists():
        raise SystemExit(f"URL 列表不存在: {url_list}")

    html_dir = Path(args.html_dir)
    md_dir = Path(args.md_dir)
    html_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)

    raw_urls = _read_urls(url_list)
    if not raw_urls:
        raise SystemExit("URL 列表为空")

    urls = [_normalize_url(u, args.base_url) for u in raw_urls]

    fetch_ok = 0
    fetch_skipped = 0
    fetch_failed = 0
    parse_ok = 0
    parse_skipped = 0
    parse_failed = 0

    for idx, url in enumerate(urls, start=1):
        slug = _slug_from_url(url)
        html_path = html_dir / f"{slug}.html"
        md_path = md_dir / f"{slug}.md"

        # Fetch step: re-entry only for HTML downloading
        try:
            if args.overwrite or not html_path.exists():
                _fetch_html(url, html_path, args.timeout, args.no_robots)
                fetch_ok += 1
            else:
                fetch_skipped += 1
                print(f"[{idx}/{len(urls)}] FETCH SKIP -> {slug}")
        except Exception as e:
            fetch_failed += 1
            print(f"[{idx}/{len(urls)}] FETCH FAIL -> {slug}: {e}", file=sys.stderr)
            if idx < len(urls) and args.sleep > 0:
                time.sleep(args.sleep)
            continue

        # Parse step (skip if markdown exists unless --overwrite)
        if not args.overwrite and md_path.exists():
            parse_skipped += 1
            print(f"[{idx}/{len(urls)}] PARSE SKIP -> {slug}")
        else:
            try:
                _parse_to_md(html_path, md_path)
                print(f"[{idx}/{len(urls)}] PARSE OK -> {slug}")
                parse_ok += 1
            except Exception as e:
                parse_failed += 1
                print(f"[{idx}/{len(urls)}] PARSE FAIL -> {slug}: {e}", file=sys.stderr)

        if idx < len(urls) and args.sleep > 0:
            time.sleep(args.sleep)

    print(
        "Done. "
        f"fetch_ok={fetch_ok}, fetch_skipped={fetch_skipped}, fetch_failed={fetch_failed}; "
        f"parse_ok={parse_ok}, parse_skipped={parse_skipped}, parse_failed={parse_failed}"
    )


if __name__ == "__main__":
    main()
