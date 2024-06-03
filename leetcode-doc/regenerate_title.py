# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : regenerate_title.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-06-03 11:42
# @UpdateTime : TODO

import os

LEETCODE_ROOT = os.environ.get("LEETCODE_ROOT", "/leetcode")

if __name__ == "__main__":
    adoc_dir = os.path.join(LEETCODE_ROOT, ".doc")

    for doc_file in os.listdir(adoc_dir):
        dot_idx = doc_file.find(".")
        no = int(doc_file[:dot_idx])
        title = doc_file[dot_idx + 1 :]
        src_file = os.path.join(adoc_dir, doc_file)
        dst_file = os.path.join(adoc_dir, f"{no:04d}.{title}")
        # print(f"mv {src_file} {dst_file}")
        os.rename(src_file, dst_file)

    cpp_dir = os.path.join(LEETCODE_ROOT, ".cpp")
    for cpp_file in os.listdir(cpp_dir):
        dot_idx = cpp_file.find(".")
        no = int(cpp_file[:dot_idx])
        title = cpp_file[dot_idx + 1 :]
        src_file = os.path.join(cpp_dir, cpp_file)
        dst_file = os.path.join(cpp_dir, f"{no:04d}.{title}")
        # print(f"mv {src_file} {dst_file}")
        os.rename(src_file, dst_file)
