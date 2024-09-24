# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : jlpt-review
# @FileName : parse_markdown.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-09-07 11:19
# @UpdateTime : TODO

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    sections = []
    current_level = 0
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("# "):
            current_level = 1
            title = line[2:]
            sections.append([title, []])
            continue
        elif line.startswith("## "):
            current_level = 2
            title = line[3:]
            sections[-1][1].append([title, []])
            continue
        elif line.startswith("### "):
            current_level = 3
            title = line[4:]
            sections[-1][1][-1][1].append([title, []])
            continue
        elif line.startswith("#### "):
            current_level = 4
            title = line[5:]
            sections[-1][1][-1][1][-1][1].append([title, []])
            continue
        if current_level == 1:
            sections[-1][1].append(line)
        elif current_level == 2:
            sections[-1][1][-1][1].append(line)
        elif current_level == 3:
            sections[-1][1][-1][1][-1][1].append(line)
        elif current_level == 4:
            sections[-1][1][-1][1][-1][1][-1][1].append(line)
    return sections

def output_markdown(sections, file_path):
    
    def _recurse(sections, level):
        output = ""
        for section in sections:
            title = section[0]
            content = section[1]
            output += "#" * level + " " + title + "\n\n"
            if content:
                if isinstance(content[0], str):
                    sorted_content = sorted(list(set(content)))
                    output += "\n".join(sorted_content) + "\n\n"
                else:
                    output += _recurse(content, level + 1)
        return output
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(_recurse(sections, 1))

if __name__ == "__main__":
    input_file = "vocabulary/index.md"
    sections = parse_markdown(input_file)
    output_markdown(sections, "vocabulary/index.md")
            