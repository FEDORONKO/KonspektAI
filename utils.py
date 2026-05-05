import os
from io import BytesIO
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdf(pdf_file):
    """
    Витягує текст із завантаженого PDF файлу.
    """
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        
        for page_num, page in enumerate(pdf_reader.pages):
            content = page.extract_text()
            if content:
                text += f"\n--- Сторінка {page_num + 1} ---\n"
                text += content
        
        if not text.strip():
            raise ValueError("PDF не містить тексту!")
        
        return text
    
    except Exception as e:
        raise Exception(f"❌ Помилка при читанні PDF: {str(e)}")


def get_text_chunks(text, chunk_size=1000, chunk_overlap=200):
    """
    Розбиває текст на чанки для RAG.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    if not chunks:
        raise ValueError("Не вдалось розбити текст на чанки!")
    
    return chunks


def validate_input(text):
    """
    Валідація вхідних даних.
    """
    if not text or len(text.strip()) == 0:
        raise ValueError("❌ Пусте повідомлення! Напишіть щось.")
    
    if len(text) > 50000:
        raise ValueError("❌ Запит занадто довгий (макс 50000 символів)!")
    
    return True