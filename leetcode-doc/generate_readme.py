# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : leetcode-doc
# @FileName : generate_readme.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-05-07 10:32
# @UpdateTime : 2024-05-07 14:32

import os
import re

LEETCODE_ROOT = os.environ.get("LEETCODE_ROOT", "/leetcode")

DOC_DIR = os.path.join(LEETCODE_ROOT, ".doc")
LOCK_DIR = os.path.join(LEETCODE_ROOT, ".lock")
CPP_DIR = os.path.join(LEETCODE_ROOT, ".cpp")

README_FILE = os.path.join(LEETCODE_ROOT, "README.md")

def extract_doc_files(doc_dir):
    doc_files = os.listdir(doc_dir)
    doc_list = []
    for doc_file in doc_files:
        if not doc_file.endswith(".md"):
            continue
        with open(os.path.join(doc_dir, doc_file), 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
        result = re.match(r'\[([0-9]+)\.(.*)\]\((.*)\)', lines[0][2:].strip())
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
            raise Exception(f"Error: {problem_id} difficulty not found")
        problem_difficulty = lines[difficulty_idx + 3].split("|")[2].strip()

        # Extract tags
        tags_idx = -1
        for idx, line in enumerate(lines[1:]):
            if "**标签**" in line:
                tags_idx = idx
                break
        if tags_idx == -1:
            continue
            # raise Exception(f"Error: {problem_id} tags not found")
        problem_tags = [it[2:].strip() for it in lines[tags_idx + 3:]]
        if len(problem_tags) == 0:
            continue

        doc_list.append([problem_id_int, {
            "id": problem_id_int,
            "id_str": problem_id_str,
            "title": problem_title,
            "identifier": problem_identifier,
            "url": problem_url,
            "doc_path": problem_doc_path,
            "difficulty": problem_difficulty,
            "tags": problem_tags,
            "is_lock": False
        }])
    doc_list = sorted(doc_list, key=lambda x: x[0])
    return doc_list

def extract_lock_files(doc_dir):
    doc_files = os.listdir(doc_dir)
    doc_list = []
    for doc_file in doc_files:
        if not doc_file.endswith(".md"):
            continue
        with open(os.path.join(doc_dir, doc_file), 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
        result = re.match(r'\[([0-9]+)\.(.*)\]\((.*)\)', lines[0][2:].strip())
        problem_id_int = int(result.group(1))
        problem_id_str = f"{problem_id_int:04d}"
        problem_title = result.group(2)
        problem_identifier = doc_file[:-3]
        problem_url = result.group(3)
        problem_doc_path = os.path.join(".lock", doc_file)

        # Extract tags
        tags_idx = -1
        for idx, line in enumerate(lines[1:]):
            if "**标签**" in line:
                tags_idx = idx
                break
        if tags_idx == -1:
            continue
            # raise Exception(f"Error: {problem_id} tags not found")
        problem_tags = [it[2:].strip() for it in lines[tags_idx + 3:]]
        if len(problem_tags) == 0:
            continue

        doc_list.append([problem_id_int, {
            "id": problem_id_int,
            "id_str": problem_id_str,
            "title": problem_title,
            "identifier": problem_identifier,
            "url": problem_url,
            "doc_path": problem_doc_path,
            "difficulty": "",
            "tags": problem_tags,
            "is_lock": True
        }])
    doc_list = sorted(doc_list, key=lambda x: x[0])
    return doc_list

def extract_cpp_files(cpp_dir, identifier):
    cpp_file = os.path.join(cpp_dir, f"{identifier}.cpp")
    if not os.path.exists(cpp_file):
        return False, ""
    return True, f".cpp/{identifier}.cpp"

def generate_markdown_table(doc_list):
    table_header = "| Title | Difficulty | Tags | Solution |\n| --- | --- | --- | --- |\n"
    table_content_list = []
    for doc in doc_list:
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
    table_content = table_header + "\n".join(table_content_list) + "\n"

    table_start_idx = 0
    table_end_idx = 0
    with open(README_FILE, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
        for idx, line in enumerate(lines):
            if "<!-- Table Start -->" in line:
                table_start_idx = idx
            if "<!-- Table End -->" in line:
                table_end_idx = idx
    with open(README_FILE, 'w', encoding='utf-8') as fp:
        fp.write("".join(lines[:table_start_idx+1]))
        fp.write(table_content)
        fp.write("".join(lines[table_end_idx:]))

if __name__ == '__main__':
    doc_list = extract_doc_files(DOC_DIR)
    lock_list = extract_lock_files(LOCK_DIR)
    rows = sorted(doc_list + lock_list, key=lambda x: x[0])
    generate_markdown_table([it[1] for it in rows])
