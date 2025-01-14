# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : leetcode-doc/check_util.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-10-29 13:00
# @UpdateTime : 2025-01-14 16:21

import os
import re

RESOURCE_ROOT = os.environ.get("RESOURCE_ROOT", "/resource")


def extract_non_algorithm_problems():
    """Extract non-algorithm problems from leetcode-tags.txt.

    Returns:
        list: A list of non-algorithm problems.
    """
    with open(f"{RESOURCE_ROOT}/leetcode-tags.txt", "r", encoding="utf-8") as fp:
        lines = fp.readlines()
    non_algorithm_list = []
    for line in lines:
        problem, tags = line.split("\t")
        tags = tags.strip()
        if tags != "Database" and tags != "Shell":
            continue
        problem_id_int = int(problem.split(".")[0])
        problem_id_str = f"{problem_id_int:04d}"
        problem_title = problem.split(".")[1]
        problem_identifier = problem.replace(".", "-")
        problem_tags = tags.strip().split("|")
        non_algorithm_list.append(
            [
                problem_id_int,
                {
                    "id": problem_id_int,
                    "id_str": problem_id_str,
                    "title": problem_title,
                    "identifier": problem_identifier,
                    "difficulty": "",
                    "tags": problem_tags,
                },
            ]
        )
    return non_algorithm_list


def extract_problem(input_string: str):
    """Extract problem information from the input string.

    Args:
        input_string (str): The input string.

    Returns:
        dict: The problem information.
    """
    pattern = r"\[\s*(\d+)\s*\] (.+) (Easy|Medium|Hard)\s+\((\d+\.\d+) %\)"
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
            "problem_id": int(problem_number),
            "title": problem_title.strip(),
            "difficulty": problem_difficulty,
            "percentage": problem_percentage,
        }
    else:
        print(f"Unable to find matching content: {input_string}")


def extract_lock_problems():
    """Extract lock problems from leetcode-problems.txt.

    Returns:
        list: A list of lock problems.
    """
    with open(f"{RESOURCE_ROOT}/leetcode-problems.txt", "r", encoding="utf-8") as fp:
        lines = fp.readlines()

    lock_list = []
    for line in reversed(lines):
        if "🔒" not in line:
            continue
        sidx = line.find("[")
        line = line[sidx:].strip()

        extract_result = extract_problem(line)
        problem_id_int = extract_result["problem_id"]
        problem_id_str = f"{problem_id_int:04d}"
        problem_title = extract_result["title"]
        problem_identifier = (
            f"{problem_id_int}-{problem_title.replace(' ', '-').lower()}"
        )
        difficulty = extract_result["difficulty"]

        lock_list.append(
            [
                problem_id_int,
                {
                    "id": problem_id_int,
                    "id_str": problem_id_str,
                    "title": problem_title,
                    "identifier": problem_identifier,
                    "difficulty": difficulty,
                    "is_lock": True,
                },
            ]
        )
    return lock_list


def extract_all_problems():
    """Extract all problems from leetcode-problems.txt.

    Returns:
        list: A list of all problems.
    """
    with open(f"{RESOURCE_ROOT}/leetcode-problems.txt", "r", encoding="utf-8") as fp:
        lines = fp.readlines()

    with open(f"{RESOURCE_ROOT}/leetcode-tags.txt", "r", encoding="utf-8") as fp:
        tags_lines = fp.readlines()

    all_list = []
    for idx, line in enumerate(reversed(lines)):
        if "🔒" in line:
            is_lock = True
        else:
            is_lock = False

        sidx = line.find("[")
        line = line[sidx:].strip()

        extract_result = extract_problem(line)
        problem_id_int = extract_result["problem_id"]
        problem_id_str = f"{problem_id_int:04d}"
        problem_title = extract_result["title"]
        problem_identifier = (
            f"{problem_id_int}-{problem_title.replace(' ', '-').lower()}"
        )
        difficulty = extract_result["difficulty"]

        tag_line = tags_lines[idx]
        problem, tags = tag_line.split("\t")
        tag_problem_id_int = int(problem.split(".")[0])
        if tag_problem_id_int != problem_id_int:
            print(f"Error: {problem_id_int} != {tag_problem_id_int}")
            break
        tags = tags.strip().split("|")

        all_list.append(
            [
                problem_id_int,
                {
                    "id": problem_id_int,
                    "id_str": problem_id_str,
                    "title": problem_title,
                    "identifier": problem_identifier,
                    "difficulty": difficulty,
                    "tags": tags,
                    "is_lock": is_lock,
                },
            ]
        )
    return all_list


if __name__ == "__main__":
    # print(extract_non_algorithm_problems())
    # print(extract_lock_problems())
    extract_all_problems()
