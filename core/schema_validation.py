def validate_dag_schema(schema: dict) -> dict:
    """
    Validates the generated JSON schema for logical errors.
    Checks for:
    1. Missing task definitions.
    2. Circular dependencies (e.g., Task A depends on Task B, which depends on Task A).
    """
    if "error" in schema:
        return schema # Already failed syntax check

    tasks = schema.get("tasks", [])
    task_ids = {task["task_id"] for task in tasks}
    
    # 1. Check for missing dependencies
    for task in tasks:
        for dependency in task.get("depends_on", []):
            if dependency not in task_ids:
                return {"error": f"Task '{task['task_id']}' depends on '{dependency}', which does not exist."}

    # 2. Check for circular dependencies using Depth First Search (DFS)
    visited = set()
    recursion_stack = set()
    
    # Create an adjacency list for the graph
    graph = {task["task_id"]: task.get("depends_on", []) for task in tasks}

    def detect_cycle(node):
        visited.add(node)
        recursion_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if detect_cycle(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True # Cycle detected!

        recursion_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if detect_cycle(node):
                return {"error": "Circular dependency detected! The workflow contains an infinite loop."}

    # If it passes all checks, return the valid schema
    return schema