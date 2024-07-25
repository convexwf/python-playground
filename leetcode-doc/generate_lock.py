# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : generate_lock.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-06-03 11:16
# @UpdateTime : TODO

import os
import re

URL = "https://leetcode.com/problems/"
problem_txt = "leetcode-problems.txt"

lock_dir = ".lock"
cpp_dir = ".lock.cpp"


def extract_problem(input_string):
    # 使用正则表达式提取题号、题目和难度
    pattern = r"\[\s*(\d+)\] (.+) (\w+)\s+\((\d+\.\d+) %\)"
    match = re.match(pattern, input_string)

    if match:
        problem_number = match.group(1)
        problem_title = match.group(2)
        problem_difficulty = match.group(3)
        problem_percentage = match.group(4)

        # print(f"题号: {problem_number}")
        # print(f"题目: {problem_title}")
        # print(f"难度: {problem_difficulty}")
        # print(f"通过率: {problem_percentage}")

        return {
            "no": int(problem_number),
            "title": problem_title.strip(),
            "difficulty": problem_difficulty,
            "percentage": problem_percentage,
        }
    else:
        print(f"未找到匹配的内容: {input_string}")


def generate_md_file(no, title):
    os.makedirs(lock_dir, exist_ok=True)
    h1_title = f"[{no}.{title}]({URL}{title.replace(' ', '-').lower()}/description/)"

    floor_ = no // 100 * 100
    ceil_ = floor_ + 99
    md_file = f"leetcode/solution/{floor_:04d}-{ceil_:04d}/{no:04d}.{title.replace(':', '')}/README_EN.md"

    desc_idx = 0
    solu_idx = 0
    with open(md_file, "r", encoding="utf-8") as f:
        md_lines = f.readlines()
        for idx, line in enumerate(md_lines):
            if line.startswith("## Description"):
                desc_idx = idx
            if line.startswith("## Solution"):
                solu_idx = idx
                break
    desc_list = md_lines[desc_idx + 1 : solu_idx]
    desc_info = "".join(desc_list).strip()

    md_info = [
        f"# {h1_title}",
        "",
        "## Description",
        "",
        desc_info,
        "",
        "## Solution",
        "",
        "**题目描述**",
        "",
        "**解题思路**",
        "",
        "**测试用例**",
        "",
        "**标签**",
        "",
    ]

    with open(
        f"{lock_dir}/{no:04d}.{title.replace(' ', '-').lower()}.md",
        "w+",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(md_info))


def generate_cpp_file(no, title):
    os.makedirs(cpp_dir, exist_ok=True)
    cpp_info = [
        "/*",
        f" * @lc app=leetcode id={no} lang=cpp",
        " *",
        f" * [{no}] {title}",
        " */",
        "",
        "// @lc code=start",
        "",
        "// @lc code=end",
        "",
    ]

    with open(
        f"{cpp_dir}/{no:04d}.{title.replace(' ', '-').lower()}.cpp",
        "w+",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(cpp_info))


if __name__ == "__main__":
    # count = 38
    # floor_ = count // 100 * 100
    # ceil_ = floor_ + 100
    # url = f"{URL}{floor_:04d}-{ceil_:04d}"

    with open(problem_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in reversed(lines):
        if "🔒" not in line:
            continue
        sidx = line.find("[")
        line = line[sidx:].strip()

        extract_result = extract_problem(line)
        no = extract_result["no"]
        title = extract_result["title"]
        difficulty = extract_result["difficulty"]

        if no > 1080:
            break

        generate_md_file(no, title)
        generate_cpp_file(no, title)
        print(f"题号: {no}, 题目: {title}, 难度: {difficulty}")
