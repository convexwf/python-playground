# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : new_crawler/test.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-15 21:23
# @UpdateTime : 2025-04-15 21:23

import ebooklib
from ebooklib import epub
from pyquery import PyQuery as pq
import datetime

# class TheEconomist(models.Model):
#     chapter_id = models.IntegerField(primary_key=True)
#     content = models.TextField()
#     title = models.CharField(max_length=100)
#     subtitle = models.CharField(max_length=100)
#     category = models.CharField(max_length=20)
#     publish_time = models.DateTimeField()
#     magazine = models.CharField(max_length=20)
#     additional_info = models.JSONField()

#     class Meta:
#         db_table = "the_economist"
#         indexes = [
#             models.Index(fields=["publish_time"]),
#             models.Index(fields=["magazine"]),
#             models.Index(fields=["category"]),
#         ]


epub_file = "tmp/The Economist 2025-07-05.epub"

if __name__ == "__main__":
    book = epub.read_epub(epub_file)

    book_title = book.get_metadata("DC", "title")[0][0]
    book_author = book.get_metadata("DC", "creator")[0][0]

    chapter_list = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content()
            content_str = content.decode("utf-8")  # Convert bytes to string
            doc = pq(content_str)
            h2_title_block = doc("div > h2")
            if h2_title_block:
                category_title = h2_title_block.text().strip()
                chapter_list.append([category_title, []])
                continue

            title_block = doc("span[class='calibre7']")
            subtitle_block = doc("span[class='calibre_11']")
            publish_time_addr_block = doc("span[class='calibre_5']")
            content_block_list = doc("p[class='calibre_4']").items()
            if not title_block or not subtitle_block:
                continue
            title = title_block.text()
            subtitle = subtitle_block.text()
            publish_time = publish_time_addr_block.text().split("|")[0].strip()
            publish_date = datetime.datetime.strptime(
                publish_time, "%b %d, %Y %I:%M %p"
            )
            chapter_content = "\n\n".join(
                [content_block.text() for content_block in content_block_list]
            ).strip()

            chapter_list[-1][1].append(
                {
                    "title": title,
                    "subtitle": subtitle,
                    "publish_time": publish_date.isoformat(),
                    "content": chapter_content,
                }
            )

    with open("tmp/chapter_list.md", "w", encoding="utf-8") as f:
        f.write(f"# {book_title}\n")
        f.write(f"Author: {book_author}\n\n")
        for category, chapters in chapter_list:
            f.write(f"## {category}\n\n")
            for chapter in chapters:
                f.write(f"### {chapter['title']}\n\n")
                f.write(f"**{chapter['subtitle']}**\n\n")
                f.write(f"Published on: {chapter['publish_time']}\n\n")
                f.write(chapter["content"] + "\n\n")

    # 获取EPUB文件中的所有图片文件名
    # for image in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    #     print("Image File: ", image.get_name())
