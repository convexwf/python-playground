# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : new_crawler/economics_parse.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-01-29 17:33
# @UpdateTime : 2025-02-07 12:40

import ebooklib
from ebooklib import epub
from pyquery import PyQuery as pq
import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()


def parse_economics_epub(epub_file, output_dir="tmp/"):
    """
    Parses an EPUB file and extracts chapter information.

    Args:
        epub_file (str): Path to the EPUB file.
        output_dir (str): Directory to save the output JSON file.
    """
    book = epub.read_epub(epub_file)

    book_title = book.get_metadata("DC", "title")[0][0]
    book_author = book.get_metadata("DC", "creator")[0][0]

    category_title = "No_Category"
    chapter_list = []
    for item in book.get_items():
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        content = item.get_body_content()
        content_str = content.decode("utf-8")  # Convert bytes to string
        doc = pq(content_str)
        h2_title_block = doc("div > h2")
        if h2_title_block:
            category_title = h2_title_block.text().strip()
            continue

        title_block = doc("span[class='calibre7']")
        subtitle_block = doc("span[class='calibre_11'], span[class='calibre_12']")
        publish_time_addr_block = doc("span[class='calibre_5']")
        content_block_list = list(doc("p[class='calibre_4']").items())
        if not title_block or not subtitle_block:
            continue
        title = title_block.text()
        subtitle = subtitle_block.text()
        publish_time = publish_time_addr_block.text().split("|")[0].strip()
        publish_date = datetime.datetime.strptime(publish_time, "%b %d, %Y %I:%M %p")

        content_list = []
        for content_block in content_block_list:
            content_list.append(content_block.text().strip())
            if content_block.text().endswith("■"):
                break
        chapter_content = "\n\n".join(content_list[2:]).strip()

        chapter_list.append(
            {
                "title": title,
                "subtitle": subtitle,
                "publish_time": publish_date.strftime("%Y-%m-%d %H:%M:%S"),
                "content": chapter_content,
                "category": category_title,
            }
        )
    output_path = os.path.join(output_dir, f"{book_title}.json")
    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(
            {
                "book_title": book_title,
                "book_author": book_author,
                "chapters": chapter_list,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    input_dir = os.getenv("ECONOMICS_INPUT_DIR")
    output_dir = os.getenv("ECONOMICS_OUTPUT_DIR")
    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        exit(1)
    for idx, filename in enumerate(reversed(os.listdir(input_dir))):
        if idx >= 10:
            break
        if not filename.endswith(".epub"):
            continue
        epub_file = os.path.join(input_dir, filename)
        print(f"Processing file: {epub_file}")
        parse_economics_epub(epub_file, output_dir=output_dir)

    # epub_file = "The Economist 2025-06-21.epub"
    # parse_economics_epub(os.path.join(input_dir, epub_file), output_dir=output_dir)
