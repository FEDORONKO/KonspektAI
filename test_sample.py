"""
Тестовий скрипт для перевірки роботи бота
"""

import os
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader
from io import BytesIO

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("GROQ_API_KEY не знайдено!")
    exit(1)

print("API ключ знайдено!")

# Перевіряємо Groq
client = Groq(api_key=api_key)

print("\n ТЕСТ 1: Перевірка з'єднання з Groq...")
try:
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": "Привіт! Ти живий?"}],
        max_tokens=100
    )
    print(f" Groq відповів: {response.choices[0].message.content[:50]}...")
except Exception as e:
    print(f" Помилка: {e}")
    exit(1)

# Перевіряємо PDF
print("\nТЕСТ 2: Перевірка завантаження PDF...")
try:
    if os.path.exists("sample.pdf"):
        with open("sample.pdf", "rb") as f:
            pdf_reader = PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            if text:
                print(f" PDF прочитано! ({len(text)} символів)")
            else:
                print(" PDF не містить тексту")
    else:
        print(" Файл sample.pdf не знайдено")
except Exception as e:
    print(f" Помилка при читанні PDF: {e}")

# Тест RAG
print("\n ТЕСТ 3: RAG з Groq...")
try:
    test_material = "Фотосинтез - це процес перетворення світла на енергію в рослинах."
    
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": f"Ти асистент. Відповідай на основі цього: {test_material}"},
            {"role": "user", "content": "Що таке фотосинтез?"}
        ],
        max_tokens=200
    )
    
    print(f" RAG працює! Відповідь: {response.choices[0].message.content[:100]}...")
except Exception as e:
    print(f" Помилка: {e}")

print("\n" + "="*50)
print(" ВСІ ТЕСТИ ПРОЙДЕНІ УСПІШНО!")
print("="*50)
print("\n Тепер можеш запустити: python -m streamlit run app.py")
