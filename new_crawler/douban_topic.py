# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : new_crawler/douban_topic.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-02-01 20:37
# @UpdateTime : 2025-02-01 20:37

import requests
from dotenv import load_dotenv
import os
from pyquery import PyQuery as pq
import datetime
import time
import random
import json

load_dotenv()


def convert_date_chinese_to_format(date_str):
    """
    Converts a Chinese date string to a datetime object.

    Args:
        date_str (str): The date string in Chinese format (e.g., "2025年7月10日").

    Returns:
        datetime.datetime: The corresponding datetime object.
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y年%m月%d日")
    except ValueError as e:
        raise ValueError(f"Date format error: {e}")


def get_topic_text(url, headers, cookies):
    """
    Fetches the douband topic text from the given URL.

    Args:
        url (str): The URL of the Douban topic.
        headers (dict): HTTP headers to use for the request.
        cookies (dict): Cookies to use for the request.

    Returns:
        str: The text content of the topic.
    """
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve the page, status code: {response.status_code}"
        )
    html_content = response.text
    doc = pq(html_content)
    doc("script").remove()  # Remove script tags

    topic_block = doc("div#link-report")
    topic_text = topic_block.text().strip()
    # Replace single newlines with double newlines for better readability
    topic_text = topic_text.replace("\n", "\n\n")

    comment_block_list = list(doc("div[class='reply-content']").items())
    translation_text = ""
    if len(comment_block_list) > 0:
        translation_text = comment_block_list[0].text().strip()
        translation_text = translation_text.replace("\n", "\n\n")

    return topic_text, translation_text


def douban_group_topic_crawler(start=0):
    """
    Crawls 【天声人語】 topic from Douban group.
    """
    url = f"https://www.douban.com/group/612024/discussion?start={start}&type=new"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }
    cookie_str = os.getenv("DOUBAN_COOKIE")
    cookies = dict(item.split("=", 1) for item in cookie_str.split("; "))
    douban_output_json = os.getenv("DOUBAN_OUTPUT_JSON", "tmp/douban_topic_list.json")

    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve the page, status code: {response.status_code} {response.text}"
        )
    html_content = response.text
    doc = pq(html_content)
    link_list = list(doc("td[class='title'] > a").items())

    topic_list = []
    existing_date_list = []
    if os.path.exists(douban_output_json):
        with open(douban_output_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            topic_list = data.get("topics", [])
            existing_date_list = [topic["date"] for topic in topic_list]

    for idx, link in enumerate(link_list):
        try:
            topic_url = link.attr("href")
            topic_title: str = link.attr("title")
            caption, chinese_date_str = topic_title.rsplit(" ", 1)
        except Exception as e:
            print(f"Error parsing link {link}: {e}")
            continue
        if not caption.startswith("【天声人語】"):
            continue
        topic_caption = caption[len("【天声人語】") :].strip()
        topic_date = convert_date_chinese_to_format(chinese_date_str)
        if topic_date.strftime("%Y-%m-%d") in existing_date_list:
            continue

        print(f"Processing topic: {topic_title} - {topic_url}")
        try:
            time.sleep(random.uniform(1, 3))  # Random sleep to avoid rate limiting
            topic_text, translation_text = get_topic_text(topic_url, headers, cookies)
            topic_list.append(
                {
                    "title": topic_caption,
                    "date": topic_date.strftime("%Y-%m-%d"),
                    "text": topic_text,
                    "translation": translation_text,
                    "href": topic_url,
                }
            )
        except Exception as e:
            print(f"Error fetching topic text: {e}")

    topic_list.sort(key=lambda x: x["date"], reverse=True)
    with open(douban_output_json, "w+", encoding="utf-8") as f:
        json.dump(
            {
                "theme": "天声人語",
                "topics": topic_list,
                "last_updated": datetime.datetime.now().isoformat(),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    douban_group_topic_crawler(start=25 * 0)
