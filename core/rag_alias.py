from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Initialize local embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db_dir = "./data/vector_db"

def initialize_knowledge_base():
    """Populates ChromaDB with SOPs, Workflow Definitions, and Tech Docs."""
    
    documents = [
        # 1. Standard Operating Procedures (SOPs)
        Document(
            page_content="Alias: SALES-DAILY-9AM. Description: Extract daily sales records from PostgreSQL, process the data to calculate total revenue, and email the summary report to the sales team.", 
            metadata={"category": "SOP", "department": "Sales"}
        ),
        Document(
            page_content="Alias: DB-BACKUP-WEEKLY. Description: Connect to the production database, compress the tables into a gzip file, and upload the backup to the AWS S3 archive bucket.", 
            metadata={"category": "SOP", "department": "IT"}
        ),
        
        # 2. Existing Workflow Definitions (giving the LLM structural hints)
        Document(
            page_content="Workflow Template for DB-BACKUP: Tasks should include 'connect_db', 'compress_data', and 'upload_to_s3'. 'compress_data' depends on 'connect_db'. 'upload_to_s3' depends on 'compress_data'.", 
            metadata={"category": "Workflow_Definition"}
        ),
        
        # 3. Technical Documentation (available Prefect tools/actions)
        Document(
            page_content="Tool: email_report. Parameters required: 'recipient_email', 'subject', 'body'. Use this action whenever a user asks to notify a team via email.", 
            metadata={"category": "Tech_Doc", "tool": "email"}
        ),
        Document(
            page_content="Tool: process_data. This task takes raw extracted data and aggregates it. It must always be preceded by an 'extract' task.", 
            metadata={"category": "Tech_Doc", "tool": "data_processing"}
        )
    ]
    
    # Load into ChromaDB and persist to disk
    vectorstore = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory=db_dir
    )
    print(f"Successfully loaded {len(documents)} documents into the RAG Knowledge Base.")
    return vectorstore