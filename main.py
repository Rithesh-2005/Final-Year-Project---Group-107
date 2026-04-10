from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn
from dotenv import load_dotenv

# Import the core modules
from core.rag_alias import setup_rag, expand_alias
from core.nlp_schema import generate_schema_with_gemini, validate_schema
from orchestration.prefect_engine import run_prefect_dag

# --- NEW: Import the database module ---
from core.database import init_db, log_execution, get_recent_logs

load_dotenv()

app = FastAPI(title="Intelligent Workflow Orchestrator")

# Initialize Databases on startup
print("Starting System Boot...")
init_db()  # <-- NEW: Boot up the SQLite logger
try:
    setup_rag()
except Exception as e:
    print(f"Warning: RAG initialization failed. Error: {e}")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

class ChatRequest(BaseModel):
    instruction: str

@app.post("/api/orchestrate")
async def orchestrate_workflow(request: ChatRequest):
    try:
        # Step 1: Context Retrieval (RAG)
        expanded_instruction = expand_alias(request.instruction)
        
        # Step 2: LLM Schema Generation (Gemini)
        raw_schema = generate_schema_with_gemini(expanded_instruction)
        
        # Step 3: Validation Safety Net
        validated_schema = validate_schema(raw_schema)
        
        # --- Handle Validation Failure ---
        if "error" in validated_schema:
            error_msg = f"Validation Failed: {validated_schema['error']}"
            
            # LOG THE FAILURE
            log_execution(
                user_command=request.instruction, 
                schema=raw_schema, 
                status=error_msg
            )
            
            return {
                "status": "failed",
                "message": "Validation Error: Could not generate a safe execution graph.",
                "error_details": validated_schema["error"],
                "schema": raw_schema
            }
            
        # ... (Steps 1, 2, and 3 remain the same) ...

        # Step 4: DAG Execution via Prefect
        # Slice the instruction to 40 characters so the UI stays clean
        short_name = request.instruction[:40] + "..." if len(request.instruction) > 40 else request.instruction
        
        # Pass the short name into the flow
        execution_results = run_prefect_dag(validated_schema, prompt_name=short_name)
        
        # --- Handle Success ---
        success_msg = "Execution Successful"
        
        # ... (Rest of your logging and return statements remain the same) ...
        
        # LOG THE SUCCESS
        log_execution(
            user_command=request.instruction, 
            schema=validated_schema, 
            status=success_msg
        )
        
        return {
            "status": "success",
            "message": f"Successfully executed workflow: {validated_schema.get('workflow_name', 'Unnamed_Workflow')}",
            "schema": validated_schema,
            "results": execution_results
        }
        
    except Exception as e:
        # LOG CRITICAL SYSTEM ERRORS
        log_execution(user_command=request.instruction, schema={}, status=f"Critical Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ... (rest of your imports and orchestrate_workflow endpoint) ...

# --- NEW: Endpoint to fetch SQLite logs for the frontend ---
@app.get("/api/logs")
def view_logs():
    """Fetches the 5 most recent audit logs from SQLite."""
    try:
        from core.database import get_recent_logs
        # Fetch the last 5 logs so the UI doesn't get too cluttered
        logs = get_recent_logs(limit=5) 
        return {"status": "success", "audit_trail": logs}
    except Exception as e:
        return {"status": "error", "message": str(e), "audit_trail": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
