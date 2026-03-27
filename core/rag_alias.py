import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Use lightweight local embeddings for the Vector DB
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db_dir = "./data/vector_db"

# Global variable to hold the vector store instance
_vectorstore = None

def setup_rag():
    """
    Populates ChromaDB with workflow Standard Operating Procedures (SOPs).
    This gives the LLM the exact context needed to generate accurate DAGs.
    """
    global _vectorstore
    
    docs = [
        Document(
            page_content="Alias: SALES-DAILY-9AM. Task: Extract daily sales records from PostgreSQL, process the data to calculate total revenue, and email the summary report to the sales team.",
            metadata={"type": "alias", "department": "Sales"}
        ),
        Document(
            page_content="Alias: DB-BACKUP. Task: Connect to production database, compress data into gzip, and upload backup to AWS S3.",
            metadata={"type": "alias", "department": "IT"}
        ),
        Document(
            page_content="Workflow Template: When processing data, it must always depend on an 'extract' or 'fetch' task. When sending an email or notification, it must depend on the processing task.",
            metadata={"type": "rule"}
        )
    ]
    
    # Initialize and persist the database
    os.makedirs("./data", exist_ok=True)
    _vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=db_dir)
    return _vectorstore

def expand_alias(user_input: str) -> str:
    """
    Searches the vector DB to expand shorthand aliases.
    Bypasses RAG if the input is a detailed, custom ad-hoc command.
    """
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(persist_directory=db_dir, embedding_function=embeddings)
        
    # LOGIC FIX: If the input is long (e.g., > 5 words), it's a custom instruction. 
    # Do not force an unrelated SOP onto it!
    if len(user_input.split()) > 5:
        return f"User Intent: {user_input}\nContextual Expansion: None (Execute as custom ad-hoc workflow)"

    results = _vectorstore.similarity_search(user_input, k=1)
    
    if results:
        return f"User Intent: {user_input}\nContextual Expansion: {results[0].page_content}"
    
    return user_input