from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import json
import os

# Ensure your HF Token is set in your environment variables
# os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your_token_here"

# UPDATE THIS to your new Hugging Face repository!
custom_model_repo = "your-username/workflow-orchestrator-mistral"

# Initialize the LLM using your fine-tuned model
llm = HuggingFaceEndpoint(
    repo_id=custom_model_repo, 
    task="text-generation",
    max_new_tokens=256,
    temperature=0.1 # Keep temperature low for structured JSON output
)

def generate_workflow_schema(expanded_instruction: str) -> dict:
    """Converts natural language into a JSON workflow schema using the fine-tuned model."""
    
    # Notice we use the exact same prompt structure used during training
    template = "<s>[INST] Convert this instruction into a workflow schema: {instruction} [/INST]"
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    # Get the raw string response from your model
    response = chain.invoke({"instruction": expanded_instruction})
    
    # Parse the JSON from the output
    try:
        # Find the boundaries of the JSON object
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response.")
            
        json_str = response[start_idx:end_idx]
        schema = json.loads(json_str)
        return schema
        
    except Exception as e:
        print(f"Parsing error: {e}")
        return {"error": "Failed to parse schema", "raw": response}