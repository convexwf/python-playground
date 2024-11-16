# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : extract_epub.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-11-16 15:56
# @UpdateTime : 2024-11-16 15:56

import os
from collections import defaultdict

import ebooklib
from ebooklib import epub
from pyquery import PyQuery as pq


def epub_to_html(epub_path, output_html_dir):
    """
    Extract the content of an epub file to html files

    :param epub_path: str, the path of the epub file
    :param output_html_dir: str, the directory to save the html files

    :return: str, the directory to save the html files
    """
    book = epub.read_epub(epub_path)
    epub_name = os.path.basename(epub_path).replace(".epub", "")
    output_dir = os.path.join(output_html_dir, epub_name)
    os.makedirs(output_dir, exist_ok=True)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content()
            content_str = content.decode("utf-8").replace("&#13;", "")

            html_filename = f"{item.get_id()}.html"
            html_path = os.path.join(output_dir, html_filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content_str)
    return output_dir


def extract_most_frequent_seven_thousand_words():
    """
    Extract the most frequent 7000 German words from the epub file

    :return: None
    """
    epub_file = "使用频率最高的7000德语单词.epub"
    output_dir = epub_to_html(epub_file, "output")

    def preprocess_content(html):
        doc = pq(html)
        doc("a").remove()
        doc('span[class="kindle-cn-specialtext-bg"]').remove()
        return doc.html()

    result = defaultdict(list)
    for _id in range(7, 23, 1):
        html_path = f"{output_dir}/id_{_id}.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
            processed_html = preprocess_content(html)
        doc = pq(processed_html)

        title, subtitle = "title", "subtitle"
        for child in doc.children():
            if child.tag == "h2":
                title = pq(child).text().strip()
            if child.tag == "h3":
                subtitle = pq(child).text().strip()
            if child.tag != "p":
                continue
            child_doc = pq(child)
            if child_doc.attr("class") and child_doc.attr("class") not in [
                "kindle-cn-para-h5"
            ]:
                continue
            word_text = (
                child_doc.text()
                .strip()
                .replace("\n", "")
                .replace("（", " (")
                .replace("）", ")")
            )
            try:
                word = word_text.split("(")[0].strip()
                word_type = word_text.split("(")[1].split(")")[0]
                word_meaning = word_text.split(")", 1)[1].strip()
                result[f"{title} - {subtitle}"].append((word, word_type, word_meaning))
            except IndexError:
                print(f"Error: {word_text}, IndexError: list index out of range")
                continue

    print(result.keys())


if __name__ == "__main__":
    extract_most_frequent_seven_thousand_words()
