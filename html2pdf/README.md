# html2pdf

The project is to convert multiple html files to a single pdf file with bookmarks.

## Prequsites

```txt
Windows 10
python 3.10.14
```

First, you need to install the whhtmltopdf tool. You can download it from [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html).

Then, you can install the required python packages by running the following command:

```bash
# Install the required python packages
$ pip install -r requirements.txt
```

## Usage

Prepare the html files in the `html` folder. Then, run the following command:

```bash
# Run the program
$ python main.py
```

The pdf file will be generated in the `pdf` folder.

```bash
$ tree .
.
├── html
│   ├── example1
│   │   ├── 1_1.html
│   │   ├── 1_2.html
│   │   └── 1_3.html
│   └── example2
│       ├── 2_1.html
│       ├── 2_2.html
│       └── 2_3.html
├── pdf
│   └── example1
│       └── 1_1.pdf
│       └── 1_2.pdf
│       └── 1_3.pdf
│   └── example2
│       └── 2_1.pdf
│       └── 2_2.pdf
│       └── 2_3.pdf
│   └── example1.pdf
│   └── example2.pdf
```

## References

- [py-pdf/pypdf: A pure-python PDF library capable of splitting, merging, cropping, and transforming the pages of PDF files](https://github.com/py-pdf/pypdf?tab=readme-ov-file)
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)
- [合并pdf文件带书签代码（利用python的PyPDF2，并解决PyPDF2 编码问题'latin-1'和PyPDF2报错：PdfReadError: EOF marker not found） - asandstar - 博客园](https://www.cnblogs.com/asandstar/p/16167531.html)
- [Python:os.path.join()产生的斜杠在Windows和Linux下的不同表现和解决方法 - WUST许志伟 - 博客园](https://www.cnblogs.com/cloud-ken/p/12666916.html)
- [PDF之pdfkit - karina梅梅 - 博客园](https://www.cnblogs.com/niejinmei/p/8157680.html)
