import re
import ebooklib
from ebooklib import epub
from html_cleaner import strip_tags


def read_and_clean_epub(epub_path):
    book = epub.read_epub(epub_path)
    RE_MULTINEWLINE = re.compile(r"(\s*?\n)+")
    RE_MULTISPACE = re.compile(r" +")

    text_out = ""
    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        text_content_with_html = doc.get_body_content().decode()
        text_content_no_html = strip_tags(text_content_with_html)
        text_content_clean = RE_MULTINEWLINE.sub("\n", text_content_no_html)
        text_content = RE_MULTISPACE.sub(" ", text_content_clean)
        text_out += text_content

    return text_out