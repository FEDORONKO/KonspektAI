import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from utils import validate_input

# Завантажуємо середовище
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY не знайдено в .env файлі!")


class EduAssistant:
    """Основний клас для роботи з RAG та LLM (Groq версія)."""
    
    def __init__(self):
        """Ініціалізація моделі та вбудувань."""
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=2000
        )
        
        # Безкоштовні вбудування від HuggingFace
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vectorstore = None
        self.retriever = None
    
    def build_knowledge_base(self, chunks):
        """
        Будує векторну базу знань з чанків тексту.
        """
        try:
            print(f"📚 Створюю базу знань з {len(chunks)} чанків...")
            
            documents = [Document(page_content=chunk) for chunk in chunks]
            
            self.vectorstore = FAISS.from_documents(
                documents,
                self.embeddings
            )
            
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            print(f"✅ База знань успішно створена!")
            return self.vectorstore
        
        except Exception as e:
            raise Exception(f"❌ Помилка при створенні бази знань: {str(e)}")
    
    def ask(self, question):
        """Задає питання боту та отримує відповідь."""
        try:
            validate_input(question)
            
            if not self.retriever:
                raise ValueError("❌ Спочатку завантажте документи!")
            
            # Отримуємо релевантні документи
            docs = self.retriever.invoke(question)
            
            # Формуємо контекст
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Промпт
            prompt = f"""На основі наступного контексту, відповідай на питання.
Якщо відповідь не міститься в контексті, скажи "Не знаю".

Контекст:
{context}

Питання: {question}

Відповідь:"""
            
            # Викликаємо LLM
            response = self.llm.invoke(prompt)
            
            return {
                "answer": response.content,
                "sources": [
                    {
                        "content": doc.page_content[:200],
                        "full_content": doc.page_content
                    }
                    for doc in docs
                ]
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "answer": "❌ Помилка при обробці запиту"
            }
    
    def generate_quiz(self, text, num_questions=5):
        """Генерує квіз на основі матеріалу."""
        try:
            prompt = f"""На основі наступного матеріалу створи {num_questions} контрольних питань для самоперевірки.

Матеріал:
{text[:2000]}

Відповідь - тільки JSON масив питань (без пояснень):
["Питання 1?", "Питання 2?", "Питання 3?"]"""
            
            response = self.llm.invoke(prompt)
            return response.content
        
        except Exception as e:
            return f"❌ Помилка: {str(e)}"