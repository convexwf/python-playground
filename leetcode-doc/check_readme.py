# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : leetcode-doc/check_readme.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-16 20:52
# @UpdateTime : 2025-04-19 21:57

import os
from collections import defaultdict

from check_util import extract_all_problems
from generate_readme import (
    extract_cpp_files,
    extract_doc_files,
    extract_lock_files,
    extract_rust_files,
)

LEETCODE_ROOT = os.environ.get("LEETCODE_ROOT", "/leetcode")
README_FILE = os.path.join(LEETCODE_ROOT, "README.md")


def generate_solved_condition(info_dict):
    # | All | Locked | Unlocked | Easy | Medium | Hard |
    # | --- | --- | --- | --- | --- | --- |
    # | 870 | 152 | 718 | 320 | 438 | 112 |

    all_count = info_dict["solved"]
    locked_count = info_dict["locked"]
    unlocked_count = all_count - locked_count
    easy_count = info_dict.get("Easy", 0)
    medium_count = info_dict.get("Medium", 0)
    hard_count = info_dict.get("Hard", 0)

    summary_content_list = [
        "| **All** | **Locked** | **Unlocked** | **Easy** | **Medium** | **Hard** |",
        "| :---: | :---: | :---: | :---: | :---: | :---: |",
        f"| {all_count} | {locked_count} | {unlocked_count} | {easy_count} | {medium_count} | {hard_count} |"
    ]
    summary_start_idx = 0
    summary_end_idx = 0
    with open(README_FILE, "r", encoding="utf-8") as fp:
        lines = fp.readlines()
        for idx, line in enumerate(lines):
            if "<!-- Summary Start -->" in line:
                summary_start_idx = idx
            if "<!-- Summary End -->" in line:
                summary_end_idx = idx
    with open(README_FILE, "w", encoding="utf-8") as fp:
        fp.write("".join(lines[: summary_start_idx + 1]))
        fp.write("\n".join(summary_content_list) + "\n")
        fp.write("".join(lines[summary_end_idx:]))



def generate_markdown_table():
    all_problems = extract_all_problems()
    solved_doc_list, not_solved_doc_list = extract_doc_files()
    solved_lock_list, not_solved_lock_list = extract_lock_files()

    solved_rows = sorted(solved_doc_list + solved_lock_list, key=lambda x: x[0])
    not_solved_rows = sorted(not_solved_doc_list + not_solved_lock_list, key=lambda x: x[0])

    table_header = (
        "| Title | Difficulty | Tags | Solution |\n| --- | --- | --- | --- |\n"
    )
    table_content_list = []
    problem_info_dict = defaultdict(int)
    problem_info_dict["solved"] = len(solved_rows)
    problem_info_dict["locked"] = len(solved_lock_list)
    code_info_dict = {}
    for row in solved_rows:
        number = row[0]
        doc = row[1]
        problem_desc = all_problems[number - 1][1]
        id_str = doc["id_str"]
        title = doc["title"]
        doc_path = doc["doc_path"]
        is_lock = doc["is_lock"]
        tags = ", ".join(doc["tags"])
        difficulty = problem_desc["difficulty"]
        percentage = problem_desc.get("percentage", "N/A") + "%"
        cpp_exist, cpp_file = extract_cpp_files(doc["identifier"])
        rust_exist, rust_file = extract_rust_files(doc["identifier"])

        problem_info_dict[difficulty] += 1
        code_info_dict[id_str] = {
            "doc_path": doc_path,
            "cpp_path": cpp_file if cpp_exist else "",
            "rust_path": rust_file if rust_exist else "",
        }


        if not is_lock:
            row_msg  = f"| [{id_str}.{title}]({doc_path}) | {difficulty} ({percentage}) | {tags} | "
        else:
            row_msg = f"| {doc['id_str']}.{doc['title']} 🔒 | {difficulty} ({percentage}) | {tags} | "
        if cpp_exist:
            row_msg += f"[cpp]({cpp_file})"
        if rust_exist:
            row_msg += f", [rust]({rust_file})"
        row_msg += " |"
        table_content_list.append(row_msg)

    for row in not_solved_rows:
        number = row[0]
        doc = row[1]
        problem_desc = all_problems[number - 1][1]
        id_str = doc["id_str"]
        title = doc["title"]
        is_lock = doc["is_lock"]
        tags = ", ".join(problem_desc.get("tags", []))
        difficulty = problem_desc["difficulty"]
        percentage = problem_desc.get("percentage", "N/A") + "%"

        if not is_lock:
            row_msg  = f"<!-- {id_str}.{title} | {difficulty} ({percentage}) | {tags} | -->"
        else:
            row_msg = f"<!-- {id_str}.{title} 🔒 | {difficulty} ({percentage}) | {tags} | -->"
        table_content_list.append(row_msg)

    table_content = table_header + "\n".join(table_content_list) + "\n"
    table_start_idx = 0
    table_end_idx = 0
    with open(README_FILE, "r", encoding="utf-8") as fp:
        lines = fp.readlines()
        for idx, line in enumerate(lines):
            if "<!-- Table Start -->" in line:
                table_start_idx = idx
            if "<!-- Table End -->" in line:
                table_end_idx = idx
    with open(README_FILE, "w", encoding="utf-8") as fp:
        fp.write("".join(lines[: table_start_idx + 1]))
        fp.write(table_content)
        fp.write("".join(lines[table_end_idx:]))
    return problem_info_dict, code_info_dict

def read_code_file(code_path):
    if not code_path:
        return ""
    cpp_file = os.path.join(LEETCODE_ROOT, code_path)
    if not os.path.exists(cpp_file):
        return ""

    with open(cpp_file, "r", encoding="utf-8") as fp:
        lines = fp.readlines()

    code_list = []
    is_code = False
    for line in lines:
        if "// @lc code=start" in line:
            is_code = True
            code_list.append([])
            continue
        if "// @lc code=end" in line:
            is_code = False
            continue
        if is_code:
            code_list[-1].append(line)
    return code_list



def generate_md_code(code_info_dict):
    # <!-- code start -->
    # <!-- code end -->
    for id_str, code_info in code_info_dict.items():
        if id_str not in ["0001", "0002", "0003"]:
            continue
        doc_path = code_info["doc_path"]

        code_content_list = ["## Code\n\n"]
        cpp_path = code_info["cpp_path"]
        cpp_list = read_code_file(cpp_path)
        if len(cpp_list) != 0:
            cpp_content_list = ["### C++\n\n"]
            for cpp_code in cpp_list:
                cpp_content_list.append("```cpp\n")
                cpp_content_list.extend(cpp_code)
                cpp_content_list.append("```\n\n")
            code_content_list.extend(cpp_content_list)
        rust_path = code_info.get("rust_path", "")
        rust_list = read_code_file(rust_path)
        if len(rust_list) != 0:
            rust_content_list = ["### Rust\n\n"]
            for rust_code in rust_list:
                rust_content_list.append("```rust\n")
                rust_content_list.extend(rust_code)
                rust_content_list.append("```\n\n")
            code_content_list.extend(rust_content_list)
        if len(code_content_list) == 1:
            continue


        with open(os.path.join(LEETCODE_ROOT, doc_path), "r+", encoding="utf-8") as fp:
            lines = fp.readlines()
        code_start_idx = -1
        code_end_idx = -1
        for idx, line in enumerate(lines):
            if "<!-- code start -->" in line:
                code_start_idx = idx
            if "<!-- code end -->" in line:
                code_end_idx = idx
        if code_start_idx == -1:
            lines.append("\n")
            code_start_idx = len(lines)
            code_end_idx = len(lines) + 1
            lines.append("<!-- code start -->\n")
            lines.append("<!-- code end -->\n")

        lines = lines[:code_start_idx + 1] + code_content_list + lines[code_end_idx:]
        with open(os.path.join(LEETCODE_ROOT, doc_path), "w", encoding="utf-8") as fp:
            fp.writelines(lines)

def clean_md_code(code_info_dict):
    for id_str, code_info in code_info_dict.items():
        if id_str not in ["0001", "0002", "0003"]:
            continue
        doc_path = code_info["doc_path"]
        with open(os.path.join(LEETCODE_ROOT, doc_path), "r+", encoding="utf-8") as fp:
            lines = fp.readlines()
        code_start_idx = -1
        code_end_idx = -1
        for idx, line in enumerate(lines):
            if "<!-- code start -->" in line and code_start_idx == -1:
                code_start_idx = idx
            if "<!-- code end -->" in line:
                code_end_idx = idx
        if code_start_idx == -1 or code_end_idx == -1:
            continue

        lines = lines[:code_start_idx + 1] + lines[code_end_idx:]
        with open(os.path.join(LEETCODE_ROOT, doc_path), "w", encoding="utf-8") as fp:
            fp.writelines(lines)


if __name__ == "__main__":
    problem_info_dict, code_info_dict = generate_markdown_table()
    generate_solved_condition(problem_info_dict)
    generate_md_code(code_info_dict)
    # clean_md_code(code_info_dict)

    # problem_list = extract_all_problems()
    # print(problem_list[:10])

    # solved_doc_list, not_solved_doc_list = extract_doc_files()
    # print(f"Total solved problems: {len(solved_doc_list)}")
    # print(f"Total not solved problems: {len(not_solved_doc_list)}")
    # print(f"Solved problems: {solved_doc_list[:10]}")
    # print(f"Not solved problems: {not_solved_doc_list[:10]}")

    # solved_doc_list, not_solved_doc_list = extract_lock_files()
    # print(f"Total solved problems: {len(solved_doc_list)}")
    # print(f"Total not solved problems: {len(not_solved_doc_list)}")
    # print(f"Solved problems: {solved_doc_list[:10]}")
    # print(f"Not solved problems: {not_solved_doc_list[:10]}")
