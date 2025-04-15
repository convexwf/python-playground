# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : openai_test/bulk_translate_task.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-03-27 16:41
# @UpdateTime : 2025-04-15 21:23

import json
from translate_task import (
    translate_english_text,
    translate_japanese_text,
    translate_german_text,
)
import datetime
import os


def get_week_end_date(year_week_str):
    """
    Converts a year-week string (e.g., "2025W27") to the end date of that week.

    Args:
        year_week_str (str): The year and week number in the format "YYYYWww".
    Returns:
        datetime.date: The date of the last day of the week (Sunday).
    """
    year_str, week_str = year_week_str.split("W")
    year = int(year_str)
    week = int(week_str)

    first_day_of_year = datetime.date(year, 1, 4)  # 1月4日总是在第一周
    # 计算该年第一个周的周一
    first_monday = first_day_of_year - datetime.timedelta(
        days=first_day_of_year.isoweekday() - 1
    )

    # 计算目标周的第一天（周一）
    week_start_date = first_monday + datetime.timedelta(weeks=week - 1)

    # 计算该周的最后一天（周日）
    week_end_date = week_start_date + datetime.timedelta(days=6)
    return week_end_date


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
    with open(md_output_path, "w+", encoding="utf-8", newline="\n") as f:
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
    topic_date = get_week_end_date(year_week)

    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    md_lines = [
        f"+++",
        f'title = "{theme} - {year_week}"',
        f"date = \"{topic_date.strftime('%Y-%m-%d')}\"",
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
    with open(md_output_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write(md_content)


def translate_nachrichtenleicht_texts(json_path, date, output_dir):
    """
    Translates Nachrichtenleicht articles from a JSON file to Chinese.

    Args:
        json_path (str): Path to the JSON file containing articles to translate.
        date (str): Date of the articles in the format "YYYY-MM-DD".
        output_dir (str): Directory to save the translated JSON file.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(json_path, "r", encoding="utf-8") as fp:
        article_list = json.load(fp)

    translated_articles = []
    for article in article_list:
        if article.get("date") != date:
            continue
        article_title = article.get("title", "Unknown Title")
        article_summary = article.get("summary", "")
        article_content = article.get("content", "")
        article_text = (
            article_title + "\n\n" + article_summary + "\n\n" + article_content
        )
        article["openai_translate"] = translate_german_text(article_text)
        translated_articles.append(article)

    output_path = os.path.join(output_dir, f"nachrichtenleicht_{date}.json")
    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(translated_articles, f, ensure_ascii=False, indent=2)


def convert_nachrichtenleicht_to_md(json_path):
    """
    Converts translated Nachrichtenleicht articles to Markdown format.

    Args:
        json_path (str): Path to the translated JSON file.
    """
    output_dir = os.path.dirname(json_path)
    filename = os.path.basename(json_path)
    filename_without_ext = os.path.splitext(filename)[0]

    with open(json_path, "r", encoding="utf-8") as fp:
        article_list = json.load(fp)

    md_lines = [
        f"+++",
        f'title = "{filename_without_ext}"',
        f"date = \"{datetime.datetime.now().strftime('%Y-%m-%d')}\"",
        f'slug = "nachrichtenleicht/{filename_without_ext.lower()}"',
        f"+++",
        "",
    ]
    for article in article_list:
        article_title = article.get("title", "Unknown Title")
        article_summary = article.get("summary", "")
        article_content = article.get("openai_translate", "")

        md_lines.append(f"## {article_title}\n\n")
        md_lines.append(f"{article_content}\n\n")

    md_content = "\n".join(md_lines)
    md_output_path = os.path.join(output_dir, f"{filename_without_ext}.md")
    with open(md_output_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write(md_content)


if __name__ == "__main__":

    # 1. Translate The Economist texts
    date = "2025-07-26"
    translate_economist_texts(
        json_path=f"tmp/The Economist/The Economist {date}.json",
        topic="Culture",
        output_dir="tmp/translated/",
    )
    convert_economist_to_md(
        json_path=f"tmp/translated/The Economist {date}_Culture.json"
    )

    # 2. Translate Douban topics
    # year_week = "2025W28"
    # translate_douban_topics_texts(
    #     json_path="tmp/Douban Topic/天声人語.json",
    #     year_week=year_week,
    #     output_dir="tmp/translated/",
    # )
    # convert_douban_topics_to_md(json_path=f"tmp/translated/天声人語_{year_week}.json")

    # 3. Translate Nachrichtenleicht articles
    # date = "2025-07-18"
    # translate_nachrichtenleicht_texts(
    #     json_path="tmp/nachrichtenleicht/nachrichtenleicht.json",
    #     date=date,
    #     output_dir="tmp/translated/",
    # )
    # convert_nachrichtenleicht_to_md(
    #     json_path=f"tmp/translated/nachrichtenleicht_{date}.json"
    # )
