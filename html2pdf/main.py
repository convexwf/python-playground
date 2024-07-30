# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-07-29 11:18
# @UpdateTime : TODO

import os
from pathlib import Path

import pdfkit
from pypdf import PdfReader, PdfWriter

wkhtmltopdf_path = "D:/software/wkhtmltopdf/bin/wkhtmltopdf.exe"
wkhtmltopdf_options = {
    "page-size": "A4",  # Letter
    "margin-top": "0.75in",
    "margin-right": "0.75in",
    "margin-bottom": "0.75in",
    "margin-left": "0.75in",
    "encoding": "UTF-8",
    "no-outline": None,
}


def _recursive_dir(target_dir):
    result_list = []

    def _resursive(target_dir, level):
        for pdf in sorted(os.listdir(target_dir)):
            parent_title = target_dir.split("/")[-1]
            pdf_path = Path(os.path.join(target_dir, pdf)).as_posix()
            if os.path.isdir(pdf_path):
                result_list.append(
                    [pdf_path, level, pdf, parent_title, sorted(os.listdir(pdf_path))]
                )
                _resursive(pdf_path, level + 1)
            else:
                result_list.append([pdf_path, level, pdf, parent_title, []])

    _resursive(target_dir, 0)
    return result_list


def merge_pdfs(pdf_root):
    pdf_list = _recursive_dir(pdf_root)
    for pdf in reversed(pdf_list):
        pdf_path = pdf[0]

        if not os.path.isdir(pdf_path):
            continue
        output_pdf = pdf_path + ".pdf"

        pdf_merger = PdfWriter()
        for pdf in sorted(os.listdir(pdf_path)):
            if not pdf.endswith(".pdf"):
                continue
            bookmark = pdf.replace(".pdf", "")
            absolute_pdf = Path(os.path.join(pdf_path, pdf)).as_posix()
            with open(absolute_pdf, "rb") as fp:
                pd = PdfReader(fp)
                # print(pdf, pd.outline)
                pdf_merger.append(pd, outline_item=bookmark, import_outline=True)
        print(f"Merge {output_pdf}")
        pdf_merger.write(output_pdf)
        # pdf_merger.write(output_pdf)
        pdf_merger.close()


def convert_html_to_pdf(html_root, output_root):
    html_list = _recursive_dir(html_root)
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    for html in html_list:
        html_path = html[0]
        level = html[1]
        html_name = html[2]
        parent_title = html[3]
        if not html_name.endswith(".html"):
            continue
        pdfkit.from_file(
            input=html_path,
            output_path="temp.pdf",
            options=wkhtmltopdf_options,
            configuration=config,
        )

        relative_path = html_path.replace(html_root, "")
        output_path = Path(output_root + relative_path).with_suffix(".pdf").as_posix()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        os.rename("temp.pdf", output_path)
        print(f"{html_path} -> {output_path}")


if __name__ == "__main__":
    input_html_root = "html"
    output_pdf_root = "pdf"

    for html_dir in os.listdir(input_html_root):
        html_path = Path(os.path.join(input_html_root, html_dir)).as_posix()
        pdf_path = Path(os.path.join(output_pdf_root, html_dir)).as_posix()
        convert_html_to_pdf(html_path, pdf_path)
    merge_pdfs(output_pdf_root)
