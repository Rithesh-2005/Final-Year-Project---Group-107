import time
from prefect import flow, task

@task(retries=1, retry_delay_seconds=2)
def execute_action(action: str, task_id: str):
    """Simulates executing a node in the DAG."""
    print(f"[{task_id}] Executing action: {action}...")
    time.sleep(2) # Simulating heavy processing
    return f"Success: {action}"

@flow(name="Dynamic-DAG-Execution", log_prints=True)
def run_prefect_dag(workflow_schema: dict):
    workflow_name = workflow_schema.get('workflow_name', 'Unnamed_Workflow')
    print(f"\n🚀 Constructing & Executing DAG for: {workflow_name}")
    
    # This dictionary will store the "Futures" (Promises of completion) for each task
    task_futures = {}
    
    for task_data in workflow_schema.get('tasks', []):
        t_id = task_data['task_id']
        action = task_data['action']
        deps = task_data.get('depends_on', [])
        
        # 1. Map the string dependencies to actual Prefect Task Futures
        # This is how Prefect knows exactly which tasks to wait for!
        upstream_futures = [task_futures[dep] for dep in deps if dep in task_futures]
        
        if upstream_futures:
            print(f"[{t_id}] Scheduled. Waiting on {deps} to finish...")
        else:
            print(f"[{t_id}] Scheduled. No dependencies, starting immediately!")
            
        # 2. Use .submit() instead of calling the function directly.
        # This tells Prefect: "Add this node to the DAG. Run it in the background 
        # ONLY AFTER the 'wait_for' tasks have successfully completed."
        future = execute_action.submit(
            action=action, 
            task_id=t_id, 
            wait_for=upstream_futures  # <-- THIS CREATES THE EDGES IN THE DAG!
        )
        
        # 3. Store the future so downstream tasks can wait for it
        task_futures[t_id] = future
        
    # Wait for all tasks in the DAG to finish before returning
    results = {t_id: future.result() for t_id, future in task_futures.items()}
    
    print(f"✅ DAG '{workflow_name}' execution completed!\n")
    return results