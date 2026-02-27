# Bridging Natural Language and Automated Workflows 🚀

**A Retrieval-Augmented LLM Framework for DAG-based Orchestration**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103%2B-009688)
![Prefect](https://img.shields.io/badge/Prefect-2.0%2B-ffffff)
![Hugging Face](https://img.shields.io/badge/HuggingFace-Models-yellow)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)

## 📖 Project Overview
[cite_start]The rising sophistication of cloud workflows calls for tools that can interpret human-level commands and automatically translate them into execution pipelines without requiring coding expertise[cite: 87, 247]. [cite_start]While tools like Apache Airflow and Prefect are powerful, they rely on manual Directed Acyclic Graph (DAG) configuration, excluding non-technical users[cite: 88, 248]. 

[cite_start]This project introduces an **Intelligent Workflow Orchestration Framework** utilizing Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to automatically generate, test, and run workflows directly from Natural Language[cite: 89, 249]. 

## 🏗️ System Architecture


[cite_start]Our framework consists of five core modules handling different stages of automation[cite: 159, 337]:
1. [cite_start]**NLP for Workflow Intents**: Interprets user inputs to identify tasks, parameters, and dependencies using pre-trained transformers via LangChain[cite: 161, 338].
2. [cite_start]**Alias Expansion using RAG**: Provides contextual grounding using a vector database (ChromaDB/FAISS) to expand shorthand aliases (e.g., `SALES-DAILY-9AM`) into detailed task descriptions[cite: 145, 167, 168, 344].
3. [cite_start]**Schema Generation & Validation**: Converts extracted intents into a machine-readable JSON/YAML schema, ensuring logical correctness and avoiding circular dependencies[cite: 164, 165, 340].
4. [cite_start]**DAG Generation & Execution**: Translates validated schemas into executable Prefect flows, forming Directed Acyclic Graphs (DAGs)[cite: 170, 347].
5. [cite_start]**Monitoring & Error Handling**: A FastAPI dashboard provides real-time status updates, while Prefect manages task scheduling, retries, and logging via SQLite[cite: 147, 172, 174, 177, 349].

## 🛠️ Tools & Technologies
* [cite_start]**Language Model:** Hugging Face Transformers (Mistral-7B / Fine-tuned TinyLlama) [cite: 180, 352]
* [cite_start]**NLP Framework:** LangChain [cite: 181, 352]
* [cite_start]**Vector Database:** ChromaDB & Sentence-Transformers [cite: 182, 352]
* [cite_start]**Orchestration Engine:** Prefect [cite: 183, 353]
* [cite_start]**Backend & API:** FastAPI [cite: 184, 353]
* [cite_start]**Database:** SQLite [cite: 185, 353]

## 📂 Repository Structure
```text
intelligent-workflow-orchestrator/
├── requirements.txt
├── main.py
├── static/
│   └── index.html               # Frontend UI Dashboard
├── core/
│   ├── __init__.py
│   ├── nlp_schema.py            # LLM Schema Generation
│   └── rag_alias.py             # ChromaDB RAG implementation
├── orchestration/
│   ├── __init__.py
│   └── prefect_engine.py        # DAG definition & Prefect flow
├── data/
│   └── vector_db/               # Local ChromaDB storage
├── scripts/
│   └── generate_dataset.py      # Synthetic JSONL data generator
└── notebooks/
    └── colab_finetuning.ipynb   # QLoRA fine-tuning code for Colab