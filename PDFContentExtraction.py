import PyPDF2
import re
import sys

# 递归提取PDF目录文件的目录信息，包括小节
def extract_toc_info(toc, level=1, parent=""):
    extracted_contents = []

    for entry in toc:
        if isinstance(entry, list):
            title = entry[1].get("/Title")
            if title:
                title_text = title.replace('\n', '').strip()
                page_num = pdf_reader.get_destination_page_number(entry[1])
                chapter_info = {
                    "chapter": f"{parent}{title_text}",
                    "page": f"pdf page = {page_num + 1} | book page = {page_num + 1}",
                    "level": level,
                }
                extracted_contents.append(chapter_info)
            if isinstance(entry[1], dict):
                # 递归提取小节信息
                extracted_contents.extend(extract_toc_info(entry[1], level + 1, parent + f"{'|' if parent else ''}"))
        else:
            break

    return extracted_contents

# 提取中文目录信息
def extract_chinese_toc(pdf_path):
    chinese_toc = []

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            try:
                text = page.extract_text()

                # 使用正则表达式匹配中文目录，这里的正则表达式根据具体文档的格式进行调整
                chapter_titles = re.findall(r'第\S+?章.*', text)
                for title in chapter_titles:
                    chinese_toc.append({"chapter": title, "page": f"pdf page = {page_num + 1} | book page = {page_num + 1}", "level": 1})
            except Exception as e:
                print(f"错误：无法从页码 {page_num + 1} 提取文本 - {e}")

    return chinese_toc

# 提取英文目录信息
def extract_english_toc(pdf_path):
    english_toc = []

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            try:
                text = page.extract_text()

                # 使用正则表达式匹配英文目录，这里的正则表达式根据具体文档的格式进行调整
                chapter_titles = re.findall(r'Chapter \d+.*', text)
                for title in chapter_titles:
                    english_toc.append({"chapter": title, "page": f"pdf page = {page_num + 1} | book page = {page_num + 1}", "level": 1})
            except Exception as e:
                print(f"错误：无法从页码 {page_num + 1} 提取文本 - {e}")

    return english_toc

# 提取整个PDF文件目录信息
def extract_chapter_info(pdf_path):
    extracted_contents = []

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        try:
            # 判断是否存在PDF目录
            if "/Outlines" in pdf_reader.trailer:
                outlines = pdf_reader.trailer['/Outlines']
                extracted_contents = extract_toc_info(outlines)
        except Exception as e:
            print(f"错误：无法提取PDF目录 - {e}")

    # 如果没有提取到目录信息，则尝试从文本内容中提取英文目录
    if not extracted_contents:
        extracted_contents = extract_english_toc(pdf_path)

    return extracted_contents

# 将提取的目录信息转化为易读的格式
def format_output(chapters):
    formatted_output = []

    def format_chapter(chapter, level):
        formatted_output.append(f"{'SUB' * (level - 1)}{chapter['chapter']} | {chapter['page']}")

    for chapter in chapters:
        format_chapter(chapter, chapter['level'])

    return formatted_output

def main(pdf_file_path):
    # 提取中文目录信息
    chinese_toc = extract_chinese_toc(pdf_file_path)

    # 输出中文目录信息
    if chinese_toc:
        print("\n提取的中文目录:")
        formatted_output = format_output(chinese_toc)
        for entry in formatted_output:
            print(entry)

    # 提取目录信息
    extracted_contents = extract_chapter_info(pdf_file_path)

    # 输出提取的目录信息
    if extracted_contents:
        print("\n提取的目录:")
        formatted_output = format_output(extracted_contents)
        for entry in formatted_output:
            print(entry)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python PDFContentExtraction.py <pdf文件>")
        sys.exit(1)

    pdf_file_path = sys.argv[1]
    main(pdf_file_path)
