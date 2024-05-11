# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : category.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-05-11 13:11
# @UpdateTime : TODO

import os
import yaml

def filter_path(path_list, problemId):
    start = min(len(path_list), problemId) - 1
    for idx in range(start, -1, -1):
        doc_id = path_list[idx][0]
        doc_title = path_list[idx][1]
        if doc_id == problemId:
            return doc_title
        if doc_id < problemId:
            break
    return ''

def gen_code(doc_list, code_list, problemId):
    lc_start = '// @lc code=start'
    lc_end = '// @lc code=end'
    docTitle = filter_path(doc_list, problemId)
    codeTitle = filter_path(code_list, problemId)
    if len(docTitle) == 0 or len(codeTitle) == 0:
        return

    docPath = os.path.join('.doc', docTitle)
    codePath = os.path.join('.code', codeTitle)
    with open(codePath, 'r', encoding='utf-8') as fp:
        codeLines = fp.readlines()

    to_write = []
    codeFlag = False
    for line in codeLines:
        if line.startswith(lc_start):
            codeFlag = True
            to_write.append('```cpp')
        elif line.startswith(lc_end):
            codeFlag = False
            to_write.append('```\n')
        elif codeFlag:
            to_write.append(line.rstrip())

    with open(docPath, 'r', encoding='utf-8') as fp:
        docLines = fp.readlines()
    codeIdx = len(docLines) - 1
    for codeIdx in range(0, len(docLines)):
        if docLines[codeIdx].startswith('**题目描述**: undefined'):
            print(f'error: {problemId} not solved')
            return
        if docLines[codeIdx].startswith('## Code'):
            docLines[codeIdx] = '## Code\n'
            break
    docLines = docLines[:codeIdx + 1] + ['\n'] + ['\n'.join(to_write)]
    with open(docPath, 'w+', encoding='utf-8', newline='\n') as fp:
        fp.writelines(docLines)

def gen_topic(doc_list):
    yaml_path = '.topic.yaml'
    with open(yaml_path, 'r', encoding="utf-8") as fp:
        fp_data = fp.read()
        data = yaml.load(fp_data, yaml.Loader)

    for _, val in data.items():
        title = val['title']
        path = val['path']
        detail = val['detail']
        problems = val['problems']

        problemLines = [f'# {title}\n', '\n']
        for problemId in problems:
            problemTitle = filter_path(doc_list, problemId)
            if len(problemTitle) == 0:
                continue
            problemPath = os.path.join('.doc', problemTitle)
            with open(problemPath, 'r', encoding='utf-8') as fp:
                lines = fp.readlines()
            lines[0] = lines[0][:3] + f'{problemId}.' + lines[0][3:]

            problemIdx = []
            for idx, line in enumerate(lines):
                if line.startswith('#'):
                    lines[idx] = '#' + line
                    problemIdx.append(idx)
            if not detail:
                lines = lines[0:2] + lines[problemIdx[2]:] + ['\n']
            problemLines = problemLines + lines
        with open(path, 'w+', encoding='utf-8', newline='\n') as fp:
            fp.write(''.join(problemLines))

def gen_summary(doc_list, detail=False):
    problemLines = [f'# summary\n', '\n']
    for doc in doc_extract:
        problemId = doc[0]
        docTitle = filter_path(doc_list, problemId)
        if len(docTitle) == 0:
            continue
        docPath = os.path.join('.doc', docTitle)

        with open(docPath, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
            lines[0] = lines[0][:3] + f'{problemId}.' + lines[0][3:]

        problemIdx = []
        solve = True
        for idx, line in enumerate(lines):
            if line.startswith('**题目描述**: undefined'):
                solve = False
                break
            if line.startswith('##'):
                lines[idx] = '==' + line.strip().split(' ')[1] + '==\n'
                problemIdx.append(idx)
            elif line.startswith('#'):
                lines[idx] = '#' + line
                problemIdx.append(idx)
        if not solve:
            print(f'error: {problemId} not solved')
            continue
        if not detail:
            lines = lines[0:2] + lines[problemIdx[2]:] + ['\n']
        problemLines = problemLines + lines

    with open('summary.md', 'w+', encoding='utf-8', newline='\n') as fp:
        fp.write(''.join(problemLines))

if __name__ == '__main__':

    doc_list = os.listdir('.doc')
    doc_extract = [[int(it.split('.')[0]), it] for it in doc_list]
    doc_extract.sort(key=lambda it:it[0])
    code_list = os.listdir('.code')
    code_extract = [[int(it.split('.')[0]), it] for it in code_list]
    code_extract.sort(key=lambda it:it[0])

    # gen_topic(doc_extract)
    for doc in doc_extract:
        gen_code(doc_extract, code_extract, doc[0])
    gen_summary(doc_extract)

