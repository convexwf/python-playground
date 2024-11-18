# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : dwds_api.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-11-18 18:16
# @UpdateTime : 2024-11-18 18:16

import json
import os

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


if __name__ == "__main__":
    fetch_goethe_words()
