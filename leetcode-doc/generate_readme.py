# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : leetcode-doc
# @FileName : generate_readme.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-05-07 10:32
# @UpdateTime : Todo

import os
import re

LEETCODE_ROOT = os.environ.get("LEETCODE_ROOT", "/home/ubuntu/work/convexwf/convex-notes/CS-notes/leetcode")

DOC_DIR = os.path.join(LEETCODE_ROOT, ".adoc")
CPP_DIR = os.path.join(LEETCODE_ROOT, ".cpp")


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

        doc_list.append([problem_id_int, {
            "id": problem_id_int,
            "id_str": problem_id_str,
            "title": problem_title,
            "identifier": problem_identifier,
            "url": problem_url,
            "doc_path": problem_doc_path,
            "difficulty": problem_difficulty,
            "tags": problem_tags
        }])
    doc_list = sorted(doc_list, key=lambda x: x[0])
    return [doc[1] for doc in doc_list]

def extract_cpp_files(cpp_dir, identifier):
    cpp_file = os.path.join(cpp_dir, f"{identifier}.cpp")
    if not os.path.exists(cpp_file):
        return False, ""
    return True, f".cpp/{identifier}.cpp"

def generate_markdown_table(doc_list):
    table_header = "| Title | Difficulty | Tags | Solution |\n| --- | --- | --- | --- |\n"
    table_content_list = []
    for doc in doc_list:
        row = f"| [{doc['id_str']}.{doc['title']}]({doc['doc_path']}) | {doc['difficulty']} | {', '.join(doc['tags'])} | "
        cpp_exist, cpp_file = extract_cpp_files(CPP_DIR, doc["identifier"])
        if cpp_exist:
            row += f"[cpp]({cpp_file}) |"
        else:
            row += " |"
        table_content_list.append(row)
    table_content = table_header + "\n".join(table_content_list) + "\n"

    table_start_idx = 0
    table_end_idx = 0
    with open("README.md", 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
        for idx, line in enumerate(lines):
            if "<!-- Table Start -->" in line:
                table_start_idx = idx
            if "<!-- Table End -->" in line:
                table_end_idx = idx
    with open("README.md", 'w', encoding='utf-8') as fp:
        fp.write("".join(lines[:table_start_idx+1]))
        fp.write(table_content)
        fp.write("".join(lines[table_end_idx:]))

if __name__ == '__main__':
    doc_list = extract_doc_files(DOC_DIR)
    generate_markdown_table(doc_list)
