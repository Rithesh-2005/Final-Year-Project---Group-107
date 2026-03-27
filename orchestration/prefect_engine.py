import time
from prefect import flow, task

# Define a generic Prefect task with automatic retries for resilience
@task(retries=1, retry_delay_seconds=2)
def execute_action(action: str, task_id: str):
    """
    Simulates executing a single node (task) in the Directed Acyclic Graph.
    In a fully integrated enterprise system, this would map to actual Python functions or API calls.
    """
    print(f"[{task_id}] Executing action: {action}...")
    
    # Simulate processing time
    time.sleep(1.5) 
    
    return f"Success: {action} completed."

@flow(name="Dynamic-DAG-Execution", log_prints=True)
def run_prefect_dag(schema: dict):
    """
    Dynamically orchestrates the workflow based on the validated JSON schema.
    """
    workflow_name = schema.get('workflow_name', 'Unnamed_Workflow')
    print(f"\n🚀 Initiating Orchestration for: {workflow_name}")
    
    results = {}
    
    # In a true asynchronous Prefect environment, we would use Future mapping 
    # to execute tasks in parallel based on `depends_on`. 
    # For this synchronous demonstration, we iterate through the validated tasks.
    for task_data in schema.get('tasks', []):
        t_id = task_data['task_id']
        action = task_data['action']
        deps = task_data.get('depends_on', [])
        
        if deps:
            print(f"[{t_id}] Dependencies met: {deps}. Triggering task.")
        else:
            print(f"[{t_id}] No dependencies. Triggering initial task.")
            
        # Execute the task
        res = execute_action(action=action, task_id=t_id)
        results[t_id] = res
        
    print(f"✅ Workflow '{workflow_name}' execution completed successfully!\n")
    return results