# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : new_crawler/economics_parse.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-01-29 17:33
# @UpdateTime : 2025-01-29 17:33

import ebooklib
from ebooklib import epub
from pyquery import PyQuery as pq
import datetime
import json


def parse_economics_epub(epub_file):
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
        subtitle_block = doc("span[class='calibre_11']")
        publish_time_addr_block = doc("span[class='calibre_5']")
        content_block_list = list(doc("p[class='calibre_4']").items())
        if not title_block or not subtitle_block:
            continue
        title = title_block.text()
        subtitle = subtitle_block.text()
        publish_time = publish_time_addr_block.text().split("|")[0].strip()
        publish_date = datetime.datetime.strptime(publish_time, "%b %d, %Y %I:%M %p")
        chapter_content = "\n\n".join(
            [content_block.text() for content_block in content_block_list[2:]]
        ).strip()

        chapter_list.append(
            {
                "title": title,
                "subtitle": subtitle,
                "publish_time": publish_date.strftime("%Y-%m-%d %H:%M:%S"),
                "content": chapter_content,
                "category": category_title,
            }
        )
    with open(f"tmp/{book_title}.json", "w", encoding="utf-8") as f:
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
    epub_file = "tmp/The Economist 2025-07-05.epub"
    parse_economics_epub(epub_file)
