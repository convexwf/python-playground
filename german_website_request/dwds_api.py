# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : dwds_api.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-11-18 18:16
# @UpdateTime : 2024-11-29 22:40

import json
import os
from collections import defaultdict

import requests

output_dir = "output"


def fetch_goethe_words():
    """
    Fetch the Goethe words from the DWDS API
    """
    base_url = "https://www.dwds.de/api/lemma/goethe/{level}.{ext}"

    csv_root = f"{output_dir}/goethe_word/csv"
    os.makedirs(csv_root, exist_ok=True)
    json_root = f"{output_dir}/goethe_word/json"
    os.makedirs(json_root, exist_ok=True)

    # csv file
    for level in ["A1", "A2", "B1"]:
        url = base_url.format(level=level, ext="csv")
        response = requests.get(url)
        response.raise_for_status()
        csv_path = f"{csv_root}/{level}.csv"
        with open(csv_path, "wb") as f:
            f.write(response.content)

    # json file
    for level in ["A1", "A2", "B1"]:
        url = base_url.format(level=level, ext="json")
        response = requests.get(url)
        response.raise_for_status()
        json_path = f"{json_root}/{level}.json"
        json_obj = response.json()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)


def fetch_word_ipa(word_list: list, count: int = 10):
    """
    Fetch the IPA of the given word list from the DWDS API
    """
    base_url = "https://www.dwds.de/api/ipa/?q={word}"

    result = []
    for idx in range(0, len(word_list), count):
        sub_list = word_list[idx : idx + count]
        url = base_url.format(word="|".join(sub_list))
        response = requests.get(url)
        response.raise_for_status()
        result.extend(response.json())
    return result


def extract_Wortarten_from_csv():
    """
    Extract the Wortarten from the csv file
    """
    csv_root = f"{output_dir}/goethe_word/csv"

    Wortarten_dict = defaultdict(int)
    for level in ["A1", "A2", "B1"]:
        csv_path = f"{csv_root}/{level}.csv"
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[1:]:
            params = line.strip().split(",")
            Wortarten = params[2]
            Wortarten_dict[Wortarten] += 1
    Wortaarten_count_list = sorted(
        Wortarten_dict.items(), key=lambda x: x[1], reverse=True
    )
    for Wortarten, count in Wortaarten_count_list:
        print(f"{Wortarten}: {count}")

    return Wortarten_dict


if __name__ == "__main__":
    # fetch_goethe_words()

    print(fetch_word_ipa(["lesen"]))
    extract_Wortarten_from_csv()
