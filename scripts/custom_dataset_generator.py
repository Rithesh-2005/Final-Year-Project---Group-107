import json
import random

# Lists of variables to create diverse synthetic prompts
systems = ["AWS", "Azure", "GCP", "Snowflake", "PostgreSQL", "MongoDB", "Salesforce", "Jira"]
actions_extract = ["Fetch", "Pull", "Extract", "Download", "Retrieve"]
data_types = ["user data", "billing logs", "sales records", "system metrics", "sensor data", "inventory levels"]
actions_process = ["clean", "transform", "process", "aggregate", "filter", "validate"]
actions_load = ["load", "upload", "save", "insert", "store"]
actions_notify = ["email the team", "send a Slack alert", "notify the admin", "generate a PDF report"]

def generate_linear_workflow():
    """Generates a simple A -> B -> C workflow."""
    sys = random.choice(systems)
    data = random.choice(data_types)
    
    instruction = f"{random.choice(actions_extract)} {data} from {sys}, then {random.choice(actions_process)} it, and finally {random.choice(actions_load)} it to the data warehouse."
    
    schema = {
        "workflow_name": f"Linear_{sys}_ETL",
        "tasks": [
            {"task_id": "t1", "action": f"extract_{data.replace(' ', '_')}", "depends_on": []},
            {"task_id": "t2", "action": f"process_data", "depends_on": ["t1"]},
            {"task_id": "t3", "action": f"load_to_warehouse", "depends_on": ["t2"]}
        ]
    }
    return instruction, schema

def generate_parallel_workflow():
    """Generates a workflow where B and C happen in parallel after A, and D waits for both."""
    sys = random.choice(systems)
    data = random.choice(data_types)
    
    instruction = f"First, {random.choice(actions_extract)} {data} from {sys}. Next, run the machine learning model and {random.choice(actions_process)} the data in parallel. Once both are done, {random.choice(actions_notify)}."
    
    schema = {
        "workflow_name": f"Parallel_{sys}_Processing",
        "tasks": [
            {"task_id": "t1", "action": f"fetch_{data.replace(' ', '_')}", "depends_on": []},
            {"task_id": "t2", "action": "run_ml_model", "depends_on": ["t1"]},
            {"task_id": "t3", "action": "process_data", "depends_on": ["t1"]},
            {"task_id": "t4", "action": "send_notification", "depends_on": ["t2", "t3"]}
        ]
    }
    return instruction, schema

def generate_two_source_workflow():
    """Generates a workflow where A and B happen independently, then C merges them."""
    sys1 = random.choice(systems)
    sys2 = random.choice([s for s in systems if s != sys1])
    
    instruction = f"Extract logs from {sys1} and download metrics from {sys2}. After both are retrieved, merge the datasets and {random.choice(actions_load)} them to the backup server."
    
    schema = {
        "workflow_name": "Merge_Two_Sources",
        "tasks": [
            {"task_id": "t1", "action": f"extract_{sys1}_logs", "depends_on": []},
            {"task_id": "t2", "action": f"download_{sys2}_metrics", "depends_on": []},
            {"task_id": "t3", "action": "merge_datasets", "depends_on": ["t1", "t2"]},
            {"task_id": "t4", "action": "load_backup", "depends_on": ["t3"]}
        ]
    }
    return instruction, schema

def format_for_mistral(instruction, schema):
    """Formats the data into the specific prompt structure required for fine-tuning."""
    schema_str = json.dumps(schema)
    formatted_text = f"<s>[INST] Convert this instruction into a workflow schema: {instruction} [/INST] {schema_str} </s>"
    return {"text": formatted_text}

def main():
    num_examples = 150
    dataset = []
    
    # Generate a mix of different workflow topologies
    for _ in range(num_examples):
        workflow_type = random.choice([generate_linear_workflow, generate_parallel_workflow, generate_two_source_workflow])
        instruction, schema = workflow_type()
        dataset.append(format_for_mistral(instruction, schema))
        
    # Write to JSONL file
    output_file = "workflow_dataset.jsonl"
    with open(output_file, "w") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Successfully generated {num_examples} synthetic workflow examples and saved to {output_file}.")
    print("Example output line:")
    print(json.dumps(dataset[0], indent=2))

if __name__ == "__main__":
    main()