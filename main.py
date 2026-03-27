from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import your modules (make sure these files exist and contain the functions we built!)
from core.rag_alias import setup_rag, expand_alias
from core.nlp_schema import generate_schema_with_gemini, validate_schema
from orchestration.prefect_engine import run_prefect_dag

app = FastAPI(title="Intelligent Workflow Orchestrator")

# 1. Initialize Vector DB on startup
print("Initializing RAG Vector Database...")
setup_rag()

# 2. Mount the static directory to serve HTML/CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. Serve the Chat Interface on the root URL
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Define the data structure expected from the frontend
class ChatRequest(BaseModel):
    instruction: str

# 4. The main endpoint that handles the workflow orchestration
@app.post("/api/orchestrate")
async def orchestrate_workflow(request: ChatRequest):
    try:
        # Step A: Context Retrieval (RAG)
        expanded_instruction = expand_alias(request.instruction)
        
        # Step B: LLM Schema Generation
        raw_schema = generate_schema_with_gemini(expanded_instruction)
        
        # Step C: Validation Safety Net
        validated_schema = validate_schema(raw_schema)
        
        if "error" in validated_schema:
            return {
                "status": "failed",
                "message": "Validation Error: Could not generate a safe execution graph.",
                "error_details": validated_schema["error"],
                "schema": raw_schema
            }
            
        # Step D: DAG Execution via Prefect
        execution_results = run_prefect_dag(validated_schema)
        
        return {
            "status": "success",
            "message": f"Successfully executed workflow: {validated_schema.get('workflow_name', 'Unnamed')}",
            "schema": validated_schema,
            "results": execution_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))