from prefect import flow, task
import time

@task(retries=2)
def execute_action(action: str):
    """Simulates executing a single task."""
    print(f"Executing: {action}")
    time.sleep(2) # Simulate work
    return f"Completed: {action}"

@flow(name="Dynamic-LLM-Workflow")
def run_dynamic_dag(schema: dict):
    """Executes the DAG based on the generated schema."""
    if "error" in schema:
        print("Invalid schema, aborting execution.")
        return
    
    print(f"Starting Workflow: {schema.get('workflow_name', 'Unnamed')}")
    task_results = {}
    
    # Simplified execution: loops through tasks and executes them. 
    # (For true parallel DAG execution in Prefect, you would map task futures).
    for task_data in schema.get('tasks', []):
        task_id = task_data['task_id']
        action = task_data['action']
        
        # Execute task
        result = execute_action(action)
        task_results[task_id] = result
        
    return task_results