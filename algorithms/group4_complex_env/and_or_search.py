import time
from core.metrics import ExperimentResult

def run_and_or_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    goal_id = context.goal_id
    broken_edges = context.broken_edges
    
    nodes_expanded = [0]
    
    def or_search(state, path):
        nodes_expanded[0] += 1
        if state == goal_id: return []
        if state in path: return None
        
        for edge in graph.nodes[state].edges:
            action = edge.target_id
            edge_tuple = tuple(sorted((state, action)))
            
            if edge_tuple in broken_edges and broken_edges[edge_tuple]['type'] != 'CROSSWALK':
                plan = and_search(state, action, path + [state])
                if plan is not None:
                    return {action: plan}
            else:
                plan = or_search(action, path + [state])
                if plan is not None:
                    return {action: plan}
        return None
        
    def and_search(state, action, path):
        nodes_expanded[0] += 1
        
        plan_if_clear = or_search(action, path)
        if plan_if_clear is None: return None
        
        plan_if_blocked = or_search(state, path)
        if plan_if_blocked is None: return None
        
        return {"if_clear": plan_if_clear, "if_blocked": plan_if_blocked}
        
    result_plan = or_search(context.start_id, [])
    exec_time = (time.perf_counter() - start_time) * 1000
    success = result_plan is not None
    
    return ExperimentResult("AND-OR Search", "Complex Env", success, exec_time, {"nodes_expanded": nodes_expanded[0]}, None)
