from fastapi import FastAPI
from pydantic import BaseModel
from core.rag_alias import expand_alias, initialize_knowledge_base
from core.nlp_schema import generate_workflow_schema
from orchestration.prefect_engine import run_dynamic_dag

app = FastAPI(title="Intelligent Workflow Orchestration Framework")

# Initialize Vector DB on startup
initialize_knowledge_base()

class WorkflowRequest(BaseModel):
    instruction: str

@app.post("/execute_workflow")
def execute_workflow(request: WorkflowRequest):
    # Step 1: RAG Alias Expansion
    expanded_instruction = expand_alias(request.instruction)
    
    # Step 2: NLP Schema Generation
    schema = generate_workflow_schema(expanded_instruction)
    
    # Step 3: DAG Execution via Prefect
    if "error" not in schema:
        execution_results = run_dynamic_dag(schema)
        return {"status": "success", "schema": schema, "results": execution_results}
    else:
        return {"status": "failed", "error": schema["error"]}