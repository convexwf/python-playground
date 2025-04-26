# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : bbc_learning_english_6min/parse_transcript_pyquery.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-24 22:15
# @UpdateTime : 2025-04-26 10:29
"""
Parse BBC Learning English local HTML -> Markdown using pyquery.
Adds hierarchy by h3 sections and includes title + publish time at top.

Usage:
    python tools/parse_transcript_pyquery.py ./data/bbc_260122.html -o ./data/bbc_260122.md
"""
import argparse
import html as html_lib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pyquery import PyQuery as pq

SPEAKER_RE = re.compile(r"^\s*([A-Za-z][A-Za-z .']{0,40})\s*:\s*(.+)$")
SPEAKER_TITLES = {"mr", "mrs", "ms", "dr", "prof", "sir", "lady"}


def extract_title(doc: pq) -> str:
    # Prefer episode h3 if present
    for el in doc("h3").items():
        txt = (el.text() or "").strip()
        if txt and txt.lower() not in {
            "6 minute english",
            "download a free 6 minute english worksheet and transcript!",
            "try our free interactive quiz!",
            "next",
        }:
            return txt
    h1 = (doc("h1").eq(0).text() or "").strip()
    if h1:
        return h1
    og = doc('meta[property="og:title"]').attr("content")
    if og:
        return og.strip()
    t = (doc("title").text() or "").strip()
    return t or "BBC Learning English - Transcript"


def extract_meta(doc: pq) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    og_url = doc('meta[property="og:url"]').attr("content")
    if og_url:
        src = og_url.strip()
        src = re.sub(r"^(https?://[^/]+)/+", r"\1/", src)
        meta["source"] = src
    for s in doc('script[type="application/ld+json"]').items():
        try:
            data = json.loads(s.text())
        except Exception:
            continue
        if (
            isinstance(data, dict)
            and data.get("@type") == "Article"
            and data.get("datePublished")
        ):
            meta["published"] = str(data.get("datePublished")).strip()
            break
    if "published" not in meta:
        art = doc('meta[property="article:published_time"]').attr("content")
        if art:
            meta["published"] = art.strip()
    return meta


def normalize_section_name(text: str) -> str:
    t = text.strip()
    lowers = t.lower()
    if "introduction" in lowers:
        return "Introduction"
    if "this week's question" in lowers:
        return "This week's question"
    if "vocabulary" in lowers:
        return "Vocabulary"
    if "transcript" in lowers:
        return "Transcript"
    return t


def _container(doc: pq) -> pq:
    c = doc("#bbcle-content .widget-container-left").eq(0)
    if not len(c):
        c = doc("#bbcle-content").eq(0)
    if not len(c):
        c = doc("body").eq(0)
    return c


def _find_h3(container: pq, title_eq: str) -> Optional[pq]:
    target = title_eq.strip().lower()
    for h in container.find("h3").items():
        txt = (h.text() or "").strip().lower()
        if txt == target or target in txt:
            return h
    return None


def _collect_vocabulary(container: pq, start_node: pq) -> List[str]:
    items: List[str] = []
    node = start_node
    for _ in range(4000):
        node = node.next()
        if not node or not len(node):
            break
        tag = getattr(node[0], "tag", "").lower()
        if tag == "h3":
            break

        def _is_transcript_marker(p: pq) -> bool:
            strong_txt = (p.find("strong").eq(0).text() or "").strip().lower()
            if strong_txt == "transcript":
                return True
            t = (p.text() or "").strip().lower()
            return t == "transcript"

        if tag in ("p", "li") and _is_transcript_marker(node):
            break
        for child_p in node.find("p").items():
            if _is_transcript_marker(child_p):
                return items

        candidates: List[pq] = []
        if tag in ("p", "li"):
            candidates.append(node)
        candidates.extend(list(node.find("p, li").items()))

        for p in candidates:
            block_html = (p.html() or "").lower()
            if block_html and "<br" in block_html and len(p.find("strong")) >= 1:
                block_items = _parse_vocabulary_block(p)
                if block_items:
                    items.extend(block_items)
                    continue

            strong = p.find("strong").eq(0)
            term = (strong.text() or "").strip()
            if not term:
                continue
            if term.strip().lower() == "transcript":
                return items
            full = (p.text() or "").strip()
            if not full:
                continue
            lines = [ln.strip() for ln in full.splitlines() if ln.strip()]
            if not lines:
                continue
            meaning_lines = (
                lines[1:]
                if lines and lines[0].strip().lower() == term.lower()
                else lines[1:]
            )
            meaning = re.sub(r"\s+", " ", " ".join(meaning_lines)).strip()
            items.append(f"VOCAB\t{term}\t{meaning}")

    return items


def _collect_after(container: pq, start_node: pq) -> List[str]:
    items: List[str] = []
    node = start_node
    for _ in range(4000):
        node = node.next()
        if not node or not len(node):
            break
        tag = getattr(node[0], "tag", "").lower()
        if tag == "h3":
            # stop also if this heading looks like a boundary (e.g., Next)
            break

        # Stop if we reached the transcript marker inside a section
        def _is_transcript_marker(p: pq) -> bool:
            strong_txt = (p.find("strong").eq(0).text() or "").strip().lower()
            if strong_txt == "transcript":
                return True
            t = (p.text() or "").strip().lower()
            return t == "transcript"

        if tag in ("p", "li") and _is_transcript_marker(node):
            break
        for child_p in node.find("p").items():
            if _is_transcript_marker(child_p):
                return items
        candidates: List[pq] = []
        if tag in ("p", "li"):
            candidates.append(node)
        candidates.extend(list(node.find("p, li").items()))
        for p in candidates:
            txt = (p.text() or "").strip()
            if not txt:
                continue
                # Filter out the transcript marker line if it slips in
                if txt.strip().lower() == "transcript":
                    continue
            cleaned = re.sub(r"\s+", " ", txt)
            if re.search(r"[A-Za-z0-9]", cleaned):
                items.append(cleaned)
    return items


def _parse_vocabulary_block(p: pq) -> List[str]:
    raw_html = (p.html() or "").strip()
    if not raw_html:
        return []

    html_text = raw_html.replace("&nbsp;", " ")
    html_text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.I)
    html_text = re.sub(
        r"<strong>\s*([^<]+?)\s*</strong>",
        r"\nTERM:\1\n",
        html_text,
        flags=re.I,
    )
    text = re.sub(r"<[^>]+>", "", html_text)
    text = html_lib.unescape(text)

    lines = [
        re.sub(r"\s+", " ", ln.replace("\u00a0", " ")).strip()
        for ln in text.splitlines()
    ]
    lines = [ln for ln in lines if ln]

    items: List[str] = []
    cur_term: Optional[str] = None
    buffer: List[str] = []

    def flush() -> None:
        nonlocal cur_term, buffer
        if cur_term:
            meaning = re.sub(r"\s+", " ", " ".join(buffer)).strip()
            items.append(f"VOCAB\t{cur_term}\t{meaning}")
        buffer = []

    for ln in lines:
        if ln.strip().lower() == "transcript":
            break
        if ln.startswith("TERM:"):
            flush()
            cur_term = ln[len("TERM:") :].strip()
            continue
        buffer.append(ln)

    flush()
    return [it for it in items if "\t" in it]


def extract_speaker_and_text(p: pq) -> Optional[Tuple[str, str]]:
    speaker = (p.find("strong").eq(0).text() or "").strip()
    if not speaker:
        return None
    full = (p.text() or "").strip()
    if full.lower().startswith(speaker.lower()):
        content = full[len(speaker) :].strip(" \u00a0:-\n\r\t")
        if content:
            return speaker, content
    return None


def _find_transcript_marker(container: pq) -> Optional[pq]:
    for h in container.find("h3").items():
        txt = (h.text() or "").strip().lower()
        if txt == "transcript":
            return h
        strong = h.find("strong").eq(0)
        if strong and (strong.text() or "").strip().lower() == "transcript":
            return h
    for p in container.find("p").items():
        strong = p.find("strong").eq(0)
        if strong and (strong.text() or "").strip().lower() == "transcript":
            return p
    return None


def _parse_transcript_block(p: pq) -> List[str]:
    raw_html = (p.html() or "").strip()
    if not raw_html:
        return []

    html_text = raw_html.replace("&nbsp;", " ")
    html_text = re.sub(
        r"<strong>\s*([^<]+?)\s*<br\s*/?>\s*</strong>",
        r"\nSPEAKER:\1\n",
        html_text,
        flags=re.I,
    )
    html_text = re.sub(
        r"<strong>\s*([^<]+?)\s*</strong>\s*<br\s*/?>",
        r"\nSPEAKER:\1\n",
        html_text,
        flags=re.I,
    )
    html_text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", html_text)
    text = html_lib.unescape(text)

    lines = [
        re.sub(r"\s+", " ", ln.replace("\u00a0", " ")).strip()
        for ln in text.splitlines()
    ]
    lines = [ln for ln in lines if ln]

    items: List[str] = []
    cur_speaker: Optional[str] = None
    buffer: List[str] = []

    def flush() -> None:
        nonlocal cur_speaker, buffer
        if cur_speaker and buffer:
            content = " ".join(buffer).strip()
            if content:
                items.append(f"SPEAKER\t{cur_speaker}\t{content}")
        elif buffer:
            for b in buffer:
                if b:
                    items.append(b)
        buffer = []

    for ln in lines:
        if ln.strip().lower() == "transcript":
            continue
        if ln.startswith("SPEAKER:"):
            flush()
            sp = ln[len("SPEAKER:") :].strip().strip(":")
            cur_speaker = sp if sp else None
            continue
        buffer.append(ln)

    flush()

    final_items: List[str] = []
    for it in items:
        if it.startswith("SPEAKER\t"):
            final_items.append(it)
            continue
        m = SPEAKER_RE.match(it)
        if m and _looks_like_speaker(m.group(1)):
            final_items.append(f"SPEAKER\t{m.group(1)}\t{m.group(2)}")
        else:
            final_items.append(it)

    return final_items


def _collect_transcript(container: pq, marker: pq) -> List[str]:
    items: List[str] = []
    node = marker
    for _ in range(8000):
        node = node.next()
        if not node or not len(node):
            break
        tag = getattr(node[0], "tag", "").lower()
        if tag == "h3":
            break
        candidates: List[pq] = []
        if tag in ("p", "li"):
            candidates.append(node)
        candidates.extend(list(node.find("p, li").items()))
        for p in candidates:
            txt = (p.text() or "").strip()
            if not txt:
                continue
            block_html = (p.html() or "").lower()
            if block_html and len(p.find("strong")) > 1 and "<br" in block_html:
                block_items = _parse_transcript_block(p)
                if block_items:
                    items.extend(block_items)
                    continue
            st = extract_speaker_and_text(p)
            if st:
                speaker, content = st
                items.append(f"SPEAKER\t{speaker}\t{content}")
            else:
                cleaned = re.sub(r"\s+", " ", txt)
                if re.search(r"[A-Za-z0-9]", cleaned):
                    items.append(cleaned)
    return items


def collect_sections(doc: pq) -> List[Tuple[str, List[str]]]:
    c = _container(doc)
    sections: List[Tuple[str, List[str]]] = []

    for sec in ("Introduction", "This week's question"):
        h = _find_h3(c, sec)
        if h is not None:
            items = _collect_after(c, h)
            if items:
                sections.append((sec, items))

    vocab_h = _find_h3(c, "Vocabulary")
    if vocab_h is not None:
        vocab_items = _collect_vocabulary(c, vocab_h)
        if vocab_items:
            sections.append(("Vocabulary", vocab_items))

    marker = _find_transcript_marker(c)
    if marker is not None:
        t_items = _collect_transcript(c, marker)
        if t_items:
            sections.append(("Transcript", t_items))

    return sections


def _md_escape_cell(text: str) -> str:
    return text.replace("|", "\\|").strip()


def _render_meta_table(meta: Dict[str, str]) -> List[str]:
    rows = []
    if meta.get("published"):
        rows.append(("Published", meta["published"]))
    if meta.get("source"):
        rows.append(("Source", meta["source"]))
    if not rows:
        return []
    out = ["| Key | Value |", "|---|---|"]
    for k, v in rows:
        out.append(f"| {_md_escape_cell(k)} | {_md_escape_cell(v)} |")
    return out


def _render_question_lines(lines_in: List[str]) -> List[str]:
    out: List[str] = []
    in_options = False
    for s in lines_in:
        s = (s or "").strip()
        if not s:
            continue

        # Split a) b) c) packed into one line (common when <br> is flattened)
        if "a)" in s and "b)" in s and re.search(r"\b[a-c]\)", s):
            idx = s.find("a)")
            prefix = s[:idx].strip() if idx > 0 else ""
            rest = s[idx:].strip() if idx >= 0 else s
            if prefix:
                out.append(prefix)

            matches = list(re.finditer(r"([a-c]\))\s*(.+?)(?=(?:\s+[a-c]\))|$)", rest))
            if matches:
                if out and out[-1] != "":
                    out.append("")
                for m in matches:
                    label = m.group(1)
                    body = re.sub(r"\s+", " ", m.group(2)).strip().rstrip(".")
                    out.append(f"- {label} {body}")
                out.append("")
                continue

        if re.match(r"^[a-c]\)\s+", s, flags=re.I):
            if out and out[-1] != "":
                out.append("")
            in_options = True
            out.append(f"- {s}")
            continue

        if in_options:
            if out and out[-1] != "":
                out.append("")
            in_options = False

        out.append(s)
    return out


def _render_vocabulary_table(items: List[str]) -> List[str]:
    rows: List[Tuple[str, str]] = []
    for s in items:
        s = (s or "").strip()
        if not s:
            continue
        if s.startswith("VOCAB\t"):
            parts = s.split("\t", 2)
            if len(parts) == 3:
                _, term, meaning = parts
                rows.append((term.strip(), meaning.strip()))
            else:
                term = parts[1].strip() if len(parts) > 1 else ""
                if term:
                    rows.append((term, ""))
            continue
        s = re.sub(r"\s+", " ", s).strip()
        parts = s.split(" ", 1)
        if len(parts) == 2 and parts[0] and parts[1]:
            rows.append((parts[0], parts[1]))
        else:
            rows.append((s, ""))
    if not rows:
        return []
    out = ["| Term | Meaning |", "|---|---|"]
    for term, meaning in rows:
        out.append(f"| {_md_escape_cell(term)} | {_md_escape_cell(meaning)} |")
    return out


def _render_transcript(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for s in items:
        if s in seen:
            continue
        seen.add(s)
        if s.startswith("SPEAKER\t"):
            parts = s.split("\t", 2)
            if len(parts) == 3:
                _, speaker, content = parts
                out.append(f"**{speaker}:** {content}  ")
            else:
                cleaned = re.sub(r"\s+", " ", s.replace("SPEAKER\t", "")).strip()
                if cleaned:
                    out.append(f"{cleaned}  ")
        else:
            if s.strip().lower() == "transcript":
                continue
            if s.lower().startswith("note:"):
                out.append(f"_{s}_  ")
            else:
                out.append(f"{s}  ")
    return out


def _looks_like_speaker(name: str) -> bool:
    name = (name or "").strip()
    if not name or "-" in name:
        return False
    words = [w for w in name.split() if w]
    if not (1 <= len(words) <= 4):
        return False
    for w in words:
        lw = w.strip(".").lower()
        if lw in SPEAKER_TITLES:
            continue
        if not w[:1].isupper():
            return False
    return True


def to_markdown(
    title: str, meta: Dict[str, str], sections: List[Tuple[str, List[str]]]
) -> str:
    lines: List[str] = [f"# {title}"]

    meta_table = _render_meta_table(meta)
    if meta_table:
        lines.append("")
        lines.extend(meta_table)

    for sec_title, items in sections:
        lines.append("")
        lines.append(f"## {sec_title}")
        lines.append("")

        if sec_title.lower() == "vocabulary":
            lines.extend(_render_vocabulary_table(items))
            continue
        if sec_title.lower() == "this week's question":
            rendered = _render_question_lines(items)
            for r in rendered:
                lines.append(r)
            continue
        if sec_title.lower() == "transcript":
            lines.extend(_render_transcript(items))
            continue

        for s in items:
            if s.strip():
                lines.append(s)

    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Parse local BBC LE HTML -> Markdown (pyquery, hierarchical)"
    )
    ap.add_argument("html", help="local HTML file path")
    ap.add_argument("-o", "--output", help="output .md file; default: stdout")
    args = ap.parse_args()

    html_path = Path(args.html)
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    doc = pq(html)

    title = extract_title(doc)
    meta = extract_meta(doc)
    sections = collect_sections(doc)

    if not sections:
        raise SystemExit("未从 HTML 中解析到有效内容，可调整选择器或规则。")

    md = to_markdown(title, meta, sections)

    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Saved -> {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
