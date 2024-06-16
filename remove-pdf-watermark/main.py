import os
from itertools import product

import fitz
from PIL import Image


# 去除pdf的水印
def remove_pdfwatermark():
    # 打开源pfd文件
    pdf_file = fitz.open("1.pdf")

    # page_no 设置为0
    page_no = 0
    modified_pages = []
    modified_pdf = fitz.open()  # Create a new PDF document
    # page在pdf文件中遍历
    for page in pdf_file:

        zoom_x = 2.5  # horizontal zoom
        zomm_y = 2.5  # vertical zoom
        mat = fitz.Matrix(zoom_x, zomm_y)  # zoom factor 2 in each dimension
        # 获取每一页对应的图片pix (pix对象类似于我们上面看到的img对象，可以读取、修改它的 RGB)
        # page.get_pixmap() 这个操作是不可逆的，即能够实现从 PDF 到图片的转换，但修改图片 RGB 后无法应用到 PDF 上，只能输出为图片
        pix = page.get_pixmap(matrix=mat)

        # 遍历图片中的宽和高，如果像素的rgb值为 192, 192, 192，就认为是水印，转换成255，255,255-->即白色
        # 192, 192, 192
        print(pix.width, pix.height)
        for pos in product(range(pix.width), range(pix.height)):
            if sum(pix.pixel(pos[0], pos[1])) >= 192 * 3:
                pix.set_pixel(pos[0], pos[1], (255, 255, 255))

        # page.set_pixmap(pix)
        pix.pil_save(f"./png/{page_no}.png", dpi=(30000, 30000))
        # 保存为pdf
        # page.set_pixmap(pix)
        # pdf_file.save("2.pdf")
        # modified_page = modified_pdf.new_page(width=pix.width, height=pix.height)
        # modified_page.insert_pixmap(fitz.IdentityMatrix, pix)

        page_no += 1

    # for page in modified_pages:
    #     modified_pdf.insert_page(page.number, page.width, page.height)

    # modified_pdf.save("2.pdf")
    # modified_pdf.close()
    # pdf_file.close()

    pdf = fitz.open()
    # 图片数字文件先转换成int类型进行排序
    img_files = sorted(os.listdir("png"), key=lambda x: int(str(x).split(".")[0]))
    for img in img_files:
        if not img.endswith(".png"):
            continue
        imgdoc = fitz.open("png/" + img)
        # 将打开后的图片转成单页pdf
        pdfbytes = imgdoc.convert_to_pdf()
        imgpdf = fitz.open("pdf", pdfbytes)
        # 将单页pdf插入到新的pdf文档中
        pdf.insert_pdf(imgpdf)
    pdf.save("2.pdf")
    pdf.close()


def remove_watermark(pdf_file_path, output_file_path):
    pdf_document = fitz.open(pdf_file_path)

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text_instances = page.search_for("帝京")

        for inst in text_instances:
            annot = page.add_redact_annot(inst)
            page.apply_redactions()

    pdf_document.save(output_file_path)
    pdf_document.close()


def remove_watermark_2(pdf_file_path, output_file_path):
    from PyPDF4 import PdfFileReader, PdfFileWriter

    output = PdfFileWriter()
    pdf = PdfFileReader(pdf_file_path, "rb")

    pdf1 = pdf.getPage(0)
    # pdf1["/Parent"]["/Kids"].clear()
    # print(pdf1["/Resources"].keys())
    content_list = pdf1["/Contents"].getObject()
    print(type(content_list))  # <class 'PyPDF4.generic.ArrayObject'>
    # remove the last element
    # content_list = content_list[:-1]
    # pdf1

    output = PdfFileWriter()
    output.addPage(pdf1)
    with open("pdf_out.pdf", "wb") as ouf:
        output.write(ouf)

    # print all the keys
    # print(pdf1.keys())
    # print(recurse_tree(pdf1))


def recurse_tree(obj, key=""):
    for i in obj.keys():
        if isinstance(obj[i], dict):
            recurse_tree(obj[i], key + i + "/")
        else:
            print(f"{key + i} : {obj[i]}")


if __name__ == "__main__":
    # remove_watermark("1.pdf", "2.pdf")
    # remove_pdfwatermark()
    remove_watermark_2("1.pdf", "2.pdf")
