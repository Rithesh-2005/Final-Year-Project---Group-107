import time
from prefect import flow, task

import time
import random
from prefect import flow, task

@task(retries=1, retry_delay_seconds=2)
def execute_action(action: str, task_id: str):
    """Simulates executing a node with realistic logging based on the action type."""
    print(f"[{task_id}] Initiating: {action}")
    
    action_lower = action.lower()
    
    # Simulate different behaviors based on the AI's generated text
    if "extract" in action_lower or "fetch" in action_lower or "retrieve" in action_lower:
        time.sleep(2)
        print(f"[{task_id}] 📦 Data successfully extracted from source (Simulated: {random.randint(5000, 15000)} rows).")
    elif "process" in action_lower or "calculate" in action_lower or "filter" in action_lower:
        time.sleep(3)
        print(f"[{task_id}] ⚙️ Data transformation complete. Null values dropped.")
    elif "email" in action_lower or "notify" in action_lower or "alert" in action_lower:
        time.sleep(1)
        print(f"[{task_id}] 📧 Notification successfully dispatched via SMTP.")
    else:
        time.sleep(1.5)
        print(f"[{task_id}] ✅ Task execution complete.")
        
    return f"Success: {action}"

# ... (Keep your run_prefect_dag function exactly the same) ...

@flow(name="Dynamic-DAG-Execution", flow_run_name="{prompt_name}", log_prints=True)
def run_prefect_dag(workflow_schema: dict, prompt_name: str = "Ad-Hoc Workflow"):
    
    workflow_name = workflow_schema.get('workflow_name', 'Unnamed_Workflow')
    print(f"\n🚀 Constructing & Executing DAG for: {workflow_name}")
    
    task_futures = {}
    
    for task_data in workflow_schema.get('tasks', []):
        t_id = task_data['task_id']
        action = task_data['action']
        deps = task_data.get('depends_on', [])
        
        upstream_futures = [task_futures[dep] for dep in deps if dep in task_futures]
        
        if upstream_futures:
            print(f"[{t_id}] Scheduled. Waiting on {deps} to finish...")
        else:
            print(f"[{t_id}] Scheduled. No dependencies, starting immediately!")
            
        future = execute_action.submit(
            action=action, 
            task_id=t_id, 
            wait_for=upstream_futures 
        )
        task_futures[t_id] = future
        
    results = {t_id: future.result() for t_id, future in task_futures.items()}
    
    print(f"✅ DAG '{workflow_name}' execution completed!\n")
    return results