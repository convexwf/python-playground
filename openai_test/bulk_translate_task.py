# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : openai_test/bulk_translate_task.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-03-27 16:41
# @UpdateTime : 2025-04-02 17:38

import json
from translate_task import translate_english_text, translate_japanese_text
import datetime
import os


def translate_economist_texts(json_path, topic, output_dir):
    """
    Translates English and Japanese texts from a JSON file to Chinese.

    Args:
        json_path (str): Path to the JSON file containing texts to translate.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    book_title = data.get("book_title", "Unknown Book")
    chapters = data.get("chapters", [])

    translated_data = []
    for chapter in chapters:
        chapter_title = chapter.get("title", "Unknown Chapter")
        chapter_subtitle = chapter.get("subtitle", "")
        chapter_content = chapter.get("content", "")
        category = chapter.get("category", "No_Category")
        publish_time = chapter.get("publish_time", "Unknown Date")
        publish_date = datetime.datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")

        if category != topic:
            continue
        chapter["openai_translate"] = translate_english_text(chapter_content)
        translated_data.append(chapter)

    output_path = os.path.join(
        output_dir,
        f"{book_title}_{topic}.json",
    )
    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)


def convert_economist_to_md(json_path):
    """
    Converts translated JSON data to Markdown format.

    Args:
        json_path (str): Path to the translated JSON file.
    """
    output_dir = os.path.dirname(json_path)
    filename = os.path.basename(json_path)
    filename_without_ext = os.path.splitext(filename)[0]
    booktitle, category = filename_without_ext.split("_")
    bookdate = booktitle.rsplit(" ", 1)[-1]

    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    md_lines = [
        f"+++",
        f'title = "{booktitle} - {category}"',
        f"date = {bookdate}",
        f"slug = \"the_economist/{booktitle.lower().replace(' ', '_')}/{category.lower()}\"",
        f"+++",
        "",
    ]
    for chapter in data:
        chapter_title = chapter.get("title", "Unknown Chapter")
        chapter_subtitle = chapter.get("subtitle", "")
        chapter_content = chapter.get("openai_translate", "")

        md_lines.append(f"## {chapter_title}\n\n")
        if chapter_subtitle:
            md_lines.append(f"*{chapter_subtitle}*\n\n")
        md_lines.append(f"{chapter_content}\n\n")
    md_content = "\n".join(md_lines)
    md_output_path = os.path.join(
        output_dir,
        f"{booktitle}_{category}.md",
    )
    with open(md_output_path, "w+", encoding="utf-8") as f:
        f.write(md_content)


def translate_douban_topics_texts(json_path, year_week, output_dir):
    """
    Translates English and Japanese texts from a JSON file to Chinese.

    Args:
        json_path (str): Path to the JSON file containing texts to translate.
        year_week (str): Year and week number in the format "2025W27".
        output_dir (str): Directory to save the translated JSON file.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    theme = data.get("theme", "No_Theme")
    translated_data = []
    for topic in data.get("topics", []):
        topic_title = topic.get("title", "Unknown Title")
        topic_date = datetime.datetime.strptime(
            topic.get("date", "Unknown Date"), "%Y-%m-%d"
        )
        topic_week, weeknum = topic.get("week").split("-")
        topic_text = topic.get("text", "")
        if topic_week != year_week or len(topic_text) <= 10:
            continue
        topic["openai_translate"] = translate_japanese_text(topic_text)
        translated_data.append(topic)

    output_path = os.path.join(
        output_dir,
        f"{theme}_{year_week}.json",
    )
    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)


def convert_douban_topics_to_md(json_path):
    """
    Converts translated JSON data to Markdown format.

    Args:
        json_path (str): Path to the translated JSON file.
    """
    output_dir = os.path.dirname(json_path)
    filename = os.path.basename(json_path)
    filename_without_ext = os.path.splitext(filename)[0]
    theme, year_week = filename_without_ext.split("_")[:2]

    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    md_lines = [
        f"+++",
        f'title = "{theme} - {year_week}"',
        f"date = {year_week}",
        f'slug = "douban_topic/{year_week.lower()}"',
        f"+++",
        "",
    ]
    for topic in data:
        topic_title = topic.get("title", "Unknown Title")
        topic_date = topic.get("date", "Unknown Date")
        topic_text = topic.get("openai_translate", "")

        md_lines.append(f"## {topic_title} ({topic_date})\n\n")
        md_lines.append(f"{topic_text}\n\n")

    md_content = "\n".join(md_lines)
    md_output_path = os.path.join(
        output_dir,
        f"{theme}_{year_week}.md",
    )
    with open(md_output_path, "w+", encoding="utf-8") as f:
        f.write(md_content)


if __name__ == "__main__":
    # translate_economics_culture_texts(
    #     json_path="tmp/The Economist/The Economist 2025-07-05.json",
    #     topic="Culture",
    #     output_dir="tmp/translated/",
    # )

    # translate_douban_topics_texts(
    #     json_path="tmp/Douban Topic/天声人語.json",
    #     year_week="2025W27",
    #     output_dir="tmp/translated/",
    # )

    translated_dir = "tmp/translated/"
    for json_file in os.listdir(translated_dir):
        if not json_file.endswith(".json"):
            continue
        if json_file.startswith("天声人語_"):
            json_path = os.path.join(translated_dir, json_file)
            convert_douban_topics_to_md(json_path=json_path)
        elif json_file.startswith("The Economist"):
            json_path = os.path.join(translated_dir, json_file)
            convert_economist_to_md(json_path=json_path)
