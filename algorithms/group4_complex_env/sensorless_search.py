import time
from collections import deque
from core.metrics import ExperimentResult

def run_sensorless_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    goal_id = context.goal_id
    
    initial_belief = frozenset([context.start_id])
    queue = deque([(initial_belief, [])])
    visited = set([initial_belief])
    nodes_expanded = 0
    
    success = False
    final_path = []
    
    while queue:
        belief, path = queue.popleft()
        nodes_expanded += 1
        
        if belief == frozenset([goal_id]):
            success = True
            final_path = path
            break
            
        possible_actions = set()
        for state in belief:
            for edge in graph.nodes[state].edges:
                possible_actions.add(edge.target_id)
                
        for action in possible_actions:
            next_belief = set()
            for state in belief:
                can_move = False
                for edge in graph.nodes[state].edges:
                    if edge.target_id == action:
                        next_belief.add(action)
                        can_move = True
                        break
                if not can_move:
                    next_belief.add(state)
                    
            next_b_frozen = frozenset(next_belief)
            if next_b_frozen not in visited:
                visited.add(next_b_frozen)
                queue.append((next_b_frozen, path + [action]))
                
    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Sensorless Search", "Complex Env", success, exec_time, {"nodes_expanded": nodes_expanded}, final_path)
