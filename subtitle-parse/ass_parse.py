# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : subtitle-parse/ass_parse.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-15 21:23
# @UpdateTime : 2025-04-15 21:23

import pysubs2
import re
import os


def rename_tv_series(config):
    # https://next-episode.net/
    with open(f"TV_series/{config}.txt", "r") as f:
        lines = f.readlines()

    name_list = []
    for line in lines[1:]:
        if not line[0].isdigit():
            name_list.append([line.strip()])
        else:
            episode = line.split("\t")[1]
            name_list[-1].append(episode.strip())


def extract_subtitle(filename):
    subs = pysubs2.load(filename, encoding="utf-16le")
    subtitle_list = []
    for event in subs.events:
        text = event.text
        text_no_styles = re.sub(r"\{.*?\}", "", text)
        parts = re.split(r"\\N", text_no_styles)

        if len(parts) != 2:
            # print(f"Error for text: {text_no_styles}")
            continue

        chinese_part = parts[0].strip()
        english_part = parts[1].strip()

        if chinese_part == "老友记":
            break
        subtitle_list.append((english_part, chinese_part))
    return subtitle_list


if __name__ == "__main__":
    root_dir = "C:/Users/convexwf/Downloads/Friends"
    for season in os.listdir(root_dir):
        season_dir = f"{root_dir}/{season}"
        info_list = [f"# Friends {season}\n"]
        for episode_idx, episode in enumerate(sorted(os.listdir(season_dir))):
            filepath = f"{season_dir}/{episode}"
            subtitle_list = extract_subtitle(filepath)
            info_list.extend(f"\n## {season}{episode_idx+1:02d}\n\n")
            for english, chinese in subtitle_list:
                if english.startswith("-"):
                    english = f"\\{english}"
                info_list.append(f"{english} / {chinese}  \n")
        with open(f"{season}.md", "w", encoding="utf-8", newline="\n") as f:
            f.writelines(info_list)

    # for filename in sorted(os.listdir(root_dir)):
    #     fiepath = os.path.join(root_dir, filename)
    #     subtitle_list = extract_subtitle(fiepath)
    #     info_list.extend(f"\n## {filename}\n\n")
    #     for english, chinese in subtitle_list:
    #         if english.startswith("-"):
    #             english = f"\\{english}"
    #         info_list.append(f"{english} / {chinese}  \n")
    # with open("output.md", "w", encoding="utf-8") as f:
    #     f.writelines(info_list)

    # if r"\N{\fn微软雅黑\fs14}" not in event.text:
    #     print(
    #         f"Start: {event.start}, End: {event.end}, Style: {event.style}, Text: {event.text}"
    #     )
