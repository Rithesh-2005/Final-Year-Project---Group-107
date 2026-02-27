from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import json
import os

# You need a free Hugging Face token: os.environ["HUGGINGFACEHUB_API_TOKEN"]
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
    task="text-generation",
    max_new_tokens=256,
    temperature=0.1
)

def generate_workflow_schema(expanded_instruction: str) -> dict:
    """Converts natural language into a JSON workflow schema."""
    template = """
    Convert the following natural language workflow instruction into a strict JSON schema.
    The JSON must have a 'workflow_name' and a 'tasks' list. Each task should have a 'task_id', 'action', and 'depends_on' (list of task_ids).
    
    Instruction: {instruction}
    
    JSON:
    """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    response = chain.invoke({"instruction": expanded_instruction})
    
    # Basic parsing to extract JSON from text (in a real scenario, use more robust regex)
    try:
        json_str = response[response.find("{"):response.rfind("}")+1]
        schema = json.loads(json_str)
        return schema
    except Exception as e:
        return {"error": "Failed to parse schema", "raw": response}