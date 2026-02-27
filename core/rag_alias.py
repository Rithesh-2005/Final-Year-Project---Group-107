from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os

# Initialize free local embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db_dir = "./data/vector_db"

def initialize_knowledge_base():
    """Populates RAG with standard workflow aliases."""
    docs = [
        Document(page_content="Alias: SALES-DAILY-9AM. Task: Fetch daily sales data from database, generate a summary report, and email it to the sales team.", metadata={"type": "alias"}),
        Document(page_content="Alias: DB-BACKUP. Task: Connect to the production database, compress the data, and upload the backup to cloud storage.", metadata={"type": "alias"})
    ]
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=db_dir)
    return vectorstore

def expand_alias(user_input: str) -> str:
    """Searches vector DB for alias expansion."""
    vectorstore = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    results = vectorstore.similarity_search(user_input, k=1)
    
    if results:
        return results[0].page_content
    return user_input # Return original if no alias found