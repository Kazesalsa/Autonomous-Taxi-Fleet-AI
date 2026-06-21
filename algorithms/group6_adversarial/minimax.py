import time
from core.metrics import ExperimentResult

def run_minimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    goal = context.goal_id
    h_fn = context.heuristic_fn
    
    nodes_expanded = [0]
    
    def terminal_test(v_node, depth):
        return v_node == goal or depth == 0
        
    def eval_fn(v_node):
        return -h_fn(graph.nodes[v_node], graph.nodes[goal])

    def max_value(v_node, s_node, blocked_edge, depth):
        nodes_expanded[0] += 1
        if terminal_test(v_node, depth): return eval_fn(v_node), None
        v = float('-inf')
        best_action = None
        for edge in graph.nodes[v_node].edges:
            nxt = edge.target_id
            e_tuple = tuple(sorted((v_node, nxt)))
            if e_tuple == blocked_edge: continue
            val, _ = min_value(nxt, s_node, None, depth - 1)
            if val > v:
                v = val
                best_action = nxt
        if best_action is None: return eval_fn(v_node), None
        return v, best_action

    def min_value(v_node, s_node, blocked_edge, depth):
        nodes_expanded[0] += 1
        if terminal_test(v_node, depth): return eval_fn(v_node), None
        v = float('inf')
        best_action = None
        
        possible_blocks = [tuple(sorted((v_node, e.target_id))) for e in graph.nodes[v_node].edges]
        if not possible_blocks: possible_blocks = [None]
        
        for block in possible_blocks:
            val, _ = max_value(v_node, s_node, block, depth - 1)
            if val < v:
                v = val
                best_action = block
        return v, best_action

    score, next_move = max_value(context.vehicle_start, context.saboteur_start, None, context.max_depth)
    
    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Minimax", "Adversarial", next_move is not None, exec_time, {"nodes_expanded": nodes_expanded[0], "score": score}, [context.vehicle_start, next_move] if next_move else [])
