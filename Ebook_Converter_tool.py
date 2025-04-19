# eBook Conversion and Processing Tool (Basic Prototype)

import os
import subprocess
from bs4 import BeautifulSoup
from docx import Document
import PyPDF2
import ebooklib
from ebooklib import epub
from textblob import TextBlob

# --- 1. Content Parsing Functions ---

def parse_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_pdf(path):
    text = ""
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def parse_html(path):
    with open(path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text(separator='\n')

# --- 2. Content Cleaning Function ---

def clean_text(text):
    blob = TextBlob(text)
    corrected = str(blob.correct())
    cleaned = "\n".join([line.strip() for line in corrected.splitlines() if line.strip()])
    return cleaned

# --- 3. ePub Creation ---

def create_epub(title, author, content, output_path):
    book = epub.EpubBook()
    book.set_title(title)
    book.add_author(author)

    chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
    chapter.content = f'<h1>{title}</h1><p>{content}</p>'
    
    book.add_item(chapter)
    book.toc = (epub.Link('chap_01.xhtml', 'Chapter 1', 'chap1'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define default style
    style = 'BODY { font-family: Arial; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    book.spine = ['nav', chapter]
    epub.write_epub(output_path, book)

# --- 4. Main Execution Function ---

def process_file(input_path, title, author, output_format='epub'):
    ext = os.path.splitext(input_path)[1].lower()
    if ext == '.docx':
        raw_text = parse_docx(input_path)
    elif ext == '.pdf':
        raw_text = parse_pdf(input_path)
    elif ext in ['.html', '.htm']: 
        raw_text = parse_html(input_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    cleaned = clean_text(raw_text)

    if output_format == 'epub':
        output_path = f"{os.path.splitext(input_path)[0]}.epub"
        create_epub(title, author, cleaned, output_path)
        print(f"ePub created at: {output_path}")
    else:
        raise ValueError("Currently only 'epub' output format is supported.")

# Example usage
if __name__ == "__main__":
    input_file = 'sample.docx'  # Change this to your test file path
    process_file(input_file, title="Sample eBook", author="Riyas")
