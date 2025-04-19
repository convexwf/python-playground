# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : leetcode-doc/generate_readme.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-05-07 10:32
# @UpdateTime : 2025-04-19 21:57

import os
import re

from check_util import (
    extract_all_problems,
    extract_lock_problems,
    extract_non_algorithm_problems,
)

LEETCODE_ROOT = os.environ.get("LEETCODE_ROOT", "/leetcode")

DOC_DIR = os.path.join(LEETCODE_ROOT, ".doc")
LOCK_DIR = os.path.join(LEETCODE_ROOT, ".lock")
CPP_DIR = os.path.join(LEETCODE_ROOT, ".cpp")
RUST_DIR = os.path.join(LEETCODE_ROOT, ".rust")

README_FILE = os.path.join(LEETCODE_ROOT, "README.md")


def extract_doc_files(doc_dir=DOC_DIR):
    """Extract doc files.

    Args:
        doc_dir (str): The doc directory.

    Returns:
        list: A list of doc files.
    """
    doc_files = os.listdir(doc_dir)
    doc_list = []
    not_solved_list = []
    for doc_file in doc_files:
        if not doc_file.endswith(".md"):
            continue
        with open(os.path.join(doc_dir, doc_file), "r", encoding="utf-8") as fp:
            lines = fp.readlines()
        result = re.match(r"\[([0-9]+)\.(.*)\]\((.*)\)", lines[0][2:].strip())
        problem_id_int = int(result.group(1))
        problem_id_str = f"{problem_id_int:04d}"
        problem_title = result.group(2)
        problem_identifier = doc_file[:-3]
        problem_url = result.group(3)
        problem_doc_path = os.path.join(".doc", doc_file)

        # Extract difficulty
        difficulty_idx = -1
        for idx, line in enumerate(lines[1:]):
            if "Difficulty" in line:
                difficulty_idx = idx
                break
        if difficulty_idx == -1:
            raise Exception(f"Error: {problem_id_int} difficulty not found")
        problem_difficulty = lines[difficulty_idx + 3].split("|")[2].strip()

        not_solved_list.append([
            problem_id_int,
            {
                "id": problem_id_int,
                "id_str": problem_id_str,
                "title": problem_title,
                "identifier": problem_identifier,
                "url": problem_url,
                "doc_path": problem_doc_path,
                "difficulty": problem_difficulty,
                "tags": [],
                "is_lock": False,
            },
        ])

        # Extract tags
        tags_start_idx = -1
        for idx, line in enumerate(lines[1:]):
            if "**标签**" in line:
                tags_start_idx = idx + 3
                break
        if tags_start_idx == -1:
            continue
        problem_tags = []
        for line in lines[tags_start_idx:]:
            if not line.startswith("- "):
                break
            problem_tag = line[2:].strip()
            problem_tags.append(problem_tag)
        if len(problem_tags) == 0:
            continue

        not_solved_list.pop()
        doc_list.append(
            [
                problem_id_int,
                {
                    "id": problem_id_int,
                    "id_str": problem_id_str,
                    "title": problem_title,
                    "identifier": problem_identifier,
                    "url": problem_url,
                    "doc_path": problem_doc_path,
                    "difficulty": problem_difficulty,
                    "tags": problem_tags,
                    "is_lock": False,
                },
            ]
        )
    doc_list = sorted(doc_list, key=lambda x: x[0])
    return doc_list, not_solved_list


def extract_lock_files(doc_dir=LOCK_DIR):
    """Extract lock files.

    Args:
        doc_dir (str): The lock directory.

    Returns:
        list: A list of lock files.
    """
    doc_files = os.listdir(doc_dir)
    solved_doc_list = []
    notsolved_doc_list = []
    for doc_file in doc_files:
        if not doc_file.endswith(".md"):
            continue
        with open(os.path.join(doc_dir, doc_file), "r", encoding="utf-8") as fp:
            lines = fp.readlines()
        result = re.match(r"\[([0-9]+)\.(.*)\]\((.*)\)", lines[0][2:].strip())
        problem_id_int = int(result.group(1))
        problem_id_str = f"{problem_id_int:04d}"
        problem_title = result.group(2)
        problem_identifier = doc_file[:-3]
        problem_url = result.group(3)
        problem_doc_path = os.path.join(".lock", doc_file)

        notsolved_doc_list.append(
            [
                problem_id_int,
                {
                    "id": problem_id_int,
                    "id_str": problem_id_str,
                    "title": problem_title,
                    "identifier": problem_identifier,
                    "url": problem_url,
                    "doc_path": problem_doc_path,
                    "difficulty": "",
                    "tags": [],
                    "is_lock": True,
                },
            ]
        )

        # Extract tags
        tags_start_idx = -1
        for idx, line in enumerate(lines[1:]):
            if "**标签**" in line:
                tags_start_idx = idx + 3
                break
        if tags_start_idx == -1:
            continue
        problem_tags = []
        for line in lines[tags_start_idx:]:
            if not line.startswith("- "):
                break
            problem_tag = line[2:].strip()
            problem_tags.append(problem_tag)
        if len(problem_tags) == 0:
            continue

        notsolved_doc_list.pop()
        solved_doc_list.append(
            [
                problem_id_int,
                {
                    "id": problem_id_int,
                    "id_str": problem_id_str,
                    "title": problem_title,
                    "identifier": problem_identifier,
                    "url": problem_url,
                    "doc_path": problem_doc_path,
                    "difficulty": "",
                    "tags": problem_tags,
                    "is_lock": True,
                },
            ]
        )
    solved_doc_list = sorted(solved_doc_list, key=lambda x: x[0])
    return solved_doc_list, notsolved_doc_list


def extract_cpp_files(identifier):
    cpp_file = os.path.join(CPP_DIR, f"{identifier}.cpp")
    if not os.path.exists(cpp_file):
        return False, ""
    return True, f".cpp/{identifier}.cpp"

def extract_rust_files(identifier):
    rust_file = os.path.join(RUST_DIR, f"{identifier}.rs")
    if not os.path.exists(rust_file):
        return False, ""
    return True, f".rust/{identifier}.rs"

def generate_solved_condition(upper_bound: int):
    """Generate solved condition.

    Args:
        upper_bound (int): The upper bound of the problem number.
    """
    solved_doc_list, _ = extract_doc_files(DOC_DIR)
    solved_lock_list = extract_lock_files(LOCK_DIR)
    lock_list = extract_lock_problems()
    non_algorithm_list = extract_non_algorithm_problems()

    solved_numbers = set([it[0] for it in solved_doc_list + solved_lock_list])
    lock_numbers = set([it[0] for it in lock_list])
    non_algorithm_numbers = set([it[0] for it in non_algorithm_list])

    solved_nonlock_count = 0
    solved_lock_count = 0
    nonlock_count = 0
    lock_count = 0
    invalid_count = 0
    for number in range(1, upper_bound + 1):
        if number in non_algorithm_numbers:
            invalid_count += 1
            continue
        if number in solved_numbers:
            if number in lock_numbers:
                solved_lock_count += 1
            else:
                solved_nonlock_count += 1
        if number in lock_numbers:
            lock_count += 1
        else:
            nonlock_count += 1
    print(f"Solved/All: {solved_nonlock_count}/{nonlock_count}")
    print(f"Solved Lock/All Lock: {solved_lock_count}/{lock_count}")
    print(f"Invalid: {invalid_count}")

    summary_content_list = [
        f"Only count the problems in the range of `[1, {upper_bound}]` .\n\n",
        f"**Accepted / Total** : **{solved_nonlock_count} / {nonlock_count}**\n\n",
        f"🔒 **Accepted / Total Lock** : **{solved_lock_count} / {lock_count}**\n\n",
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
        fp.writelines(summary_content_list)
        fp.write("".join(lines[summary_end_idx:]))


def generate_markdown_table(upper_bound: int):
    all_problems = extract_all_problems()
    solved_doc_list, not_solved_doc_list = extract_doc_files(DOC_DIR)
    solved_lock_list, not_solved_doc_list = extract_lock_files(LOCK_DIR)
    rows = sorted(solved_doc_list + solved_lock_list, key=lambda x: x[0])
    solved_numbers = set([it[0] for it in rows])
    solved_items = [it[1] for it in rows]
    non_algorithm_list = extract_non_algorithm_problems()
    non_algorithm_numbers = set([it[0] for it in non_algorithm_list])

    table_header = (
        "| Title | Difficulty | Tags | Solution |\n| --- | --- | --- | --- |\n"
    )
    table_content_list = []
    for doc in solved_items:
        if not doc["is_lock"]:
            row = f"| [{doc['id_str']}.{doc['title']}]({doc['doc_path']}) | {doc['difficulty']} | {', '.join(doc['tags'])} | "
        else:
            row = f"| {doc['id_str']}.{doc['title']} 🔒 | | {', '.join(doc['tags'])} | "
        cpp_exist, cpp_file = extract_cpp_files(CPP_DIR, doc["identifier"])
        if cpp_exist:
            row += f"[cpp]({cpp_file}) |"
        else:
            row += " |"
        table_content_list.append(row)

    for number in range(1, upper_bound + 1):
        if number in solved_numbers:
            continue
        elif number in non_algorithm_numbers:
            continue
        else:
            problem_item = all_problems[number - 1][1]
            if problem_item["is_lock"]:
                row = f"<!-- {problem_item['id_str']}.{problem_item['title']} 🔒 | {problem_item['difficulty']} | {', '.join(problem_item['tags'])} | -->"
            else:
                row = f"<!-- {problem_item['id_str']}.{problem_item['title']} | {problem_item['difficulty']} | {', '.join(problem_item['tags'])} | -->"
            table_content_list.append(row)

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


if __name__ == "__main__":
    generate_solved_condition(1080)
    generate_markdown_table(1080)
