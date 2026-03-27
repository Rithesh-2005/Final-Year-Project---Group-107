import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Initialize Gemini 1.5 Flash
# Note: Ensure GOOGLE_API_KEY is set in your environment variables before running
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0.1, # Low temperature for deterministic, structured output
        max_retries=2
    )
except Exception as e:
    print(f"Warning: Failed to initialize Gemini. Ensure GOOGLE_API_KEY is set. Error: {e}")
    llm = None

def generate_schema_with_gemini(instruction: str) -> dict:
    """
    Uses Gemini to convert the natural language instruction into a structured JSON DAG schema.
    """
    if not llm:
        return {"error": "LLM not initialized. Check API Key."}

    template = """
    Convert the following natural language workflow instruction into a strict JSON schema.
    The JSON MUST have a 'workflow_name' and a 'tasks' list. 
    Each task should have a 'task_id', 'action', and 'depends_on' (a list of task_ids it must wait for).
    
    Return ONLY valid JSON. Do not include markdown formatting like ```json or backticks.

    Instruction: {instruction}
    """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"instruction": instruction})
        
        # Clean up potential markdown formatting from the LLM response
        output_text = response.content.strip()
        if output_text.startswith("```json"):
            output_text = output_text[7:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]
            
        schema = json.loads(output_text.strip())
        return schema
        
    except Exception as e:
        return {"error": f"Failed to generate or parse JSON: {e}"}

def validate_schema(schema: dict) -> dict:
    """
    Validates the generated schema to ensure logical correctness.
    Checks for missing tasks and circular dependencies (infinite loops).
    """
    if "error" in schema: 
        return schema
    
    tasks = schema.get("tasks", [])
    if not tasks:
        return {"error": "Schema generated successfully, but no tasks were identified."}

    task_ids = {t["task_id"] for t in tasks}
    
    # 1. Check for missing dependencies
    for task in tasks:
        for dep in task.get("depends_on", []):
            if dep not in task_ids:
                return {"error": f"Task '{task['task_id']}' depends on '{dep}', which does not exist in the workflow."}

    # 2. Check for circular dependencies using Depth First Search (DFS)
    visited = set()
    recursion_stack = set()
    graph = {t["task_id"]: t.get("depends_on", []) for t in tasks}

    def detect_cycle(node):
        visited.add(node)
        recursion_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if detect_cycle(neighbor): 
                    return True
            elif neighbor in recursion_stack:
                return True
        recursion_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if detect_cycle(node):
                return {"error": "Circular dependency detected! The execution graph contains an infinite loop."}
                
    # Schema is safe and logical
    return schema