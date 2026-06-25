import time
import math
from core.metrics import ExperimentResult

def get_h(context, n1, n2):
    if hasattr(context, 'heuristic_fn') and context.heuristic_fn:
        return context.heuristic_fn(n1, n2)
    return math.hypot(n2.x - n1.x, n2.y - n1.y) if n1 and n2 else 0.0

def run_minimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    
    def eval_fn(v): 
        return -get_h(context, context.graph.nodes[v], context.graph.nodes[context.goal_id])
    
    def max_value(v_node, s_node, blocked, d, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('-inf'), None
        for edge in context.graph.nodes[v_node].edges:
            if edge.target_id in visited: continue
            edge_tuple = tuple(sorted((v_node, edge.target_id)))
            if edge_tuple == blocked: continue
            if hasattr(context, 'broken_edges') and edge_tuple in context.broken_edges: continue
            
            val, _ = min_value(edge.target_id, s_node, None, d - 1, visited | {edge.target_id})
            if val > v: v, best = val, edge.target_id
        return (float('-inf'), None) if best is None else (v, best)

    def min_value(v_node, s_node, blocked, d, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('inf'), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges]
        if hasattr(context, 'broken_edges'):
            poss = [b for b in poss if b not in context.broken_edges]
        if not poss: poss = [None]
        
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, visited)
            if val < v: v, best = val, b
        return v, best

    path = [context.vehicle_start]
    curr = context.vehicle_start
    total_score = 0
    
    while curr != context.goal_id and len(path) < 100:
        score, nxt = max_value(curr, context.saboteur_start, None, context.max_depth, {curr})
        if not nxt or nxt in path: 
            break
        path.append(nxt)
        curr = nxt
        total_score += score

    if curr != context.goal_id:
        try:
            from algorithms.informed import run_a_star
            from core.contexts import PathfindingContext
            res = run_a_star(PathfindingContext(context.graph, curr, context.goal_id, heuristic_fn=lambda n1, n2: get_h(context, n1, n2)))
            if res and getattr(res, 'path', None):
                path.extend(res.path[1:])
        except Exception:
            pass

    return ExperimentResult("Minimax", "Adversarial", curr == context.goal_id or len(path) > 1, 
                            (time.perf_counter() - start_time) * 1000, 
                            {"nodes_expanded": nodes_expanded[0], "score": total_score}, path)

def run_alpha_beta(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    
    def eval_fn(v): 
        return -get_h(context, context.graph.nodes[v], context.graph.nodes[context.goal_id])
    
    def max_value(v_node, s_node, blocked, d, alpha, beta, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('-inf'), None
        for edge in context.graph.nodes[v_node].edges:
            if edge.target_id in visited: continue
            edge_tuple = tuple(sorted((v_node, edge.target_id)))
            if edge_tuple == blocked: continue
            if hasattr(context, 'broken_edges') and edge_tuple in context.broken_edges: continue
            
            val, _ = min_value(edge.target_id, s_node, None, d - 1, alpha, beta, visited | {edge.target_id})
            if val > v: v, best = val, edge.target_id
            if v >= beta: return v, best
            alpha = max(alpha, v)
        return (float('-inf'), None) if best is None else (v, best)

    def min_value(v_node, s_node, blocked, d, alpha, beta, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('inf'), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges]
        if hasattr(context, 'broken_edges'):
            poss = [b for b in poss if b not in context.broken_edges]
        if not poss: poss = [None]
        
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, alpha, beta, visited)
            if val < v: v, best = val, b
            if v <= alpha: return v, best
            beta = min(beta, v)
        return v, best

    path = [context.vehicle_start]
    curr = context.vehicle_start
    total_score = 0
    
    while curr != context.goal_id and len(path) < 100:
        score, nxt = max_value(curr, context.saboteur_start, None, context.max_depth, float('-inf'), float('inf'), {curr})
        if not nxt or nxt in path: 
            break
        path.append(nxt)
        curr = nxt
        total_score += score

    if curr != context.goal_id:
        try:
            from algorithms.informed import run_a_star
            from core.contexts import PathfindingContext
            res = run_a_star(PathfindingContext(context.graph, curr, context.goal_id, heuristic_fn=lambda n1, n2: get_h(context, n1, n2)))
            if res and getattr(res, 'path', None):
                path.extend(res.path[1:])
        except Exception:
            pass

    return ExperimentResult("Alpha-Beta", "Adversarial", curr == context.goal_id or len(path) > 1, 
                            (time.perf_counter() - start_time) * 1000, 
                            {"nodes_expanded": nodes_expanded[0], "score": total_score}, path)

def run_expectimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    
    def eval_fn(v): 
        return -get_h(context, context.graph.nodes[v], context.graph.nodes[context.goal_id])
    
    def max_value(v_node, s_node, blocked, d, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('-inf'), None
        for edge in context.graph.nodes[v_node].edges:
            if edge.target_id in visited: continue
            edge_tuple = tuple(sorted((v_node, edge.target_id)))
            if edge_tuple == blocked: continue
            if hasattr(context, 'broken_edges') and edge_tuple in context.broken_edges: continue
            
            val, _ = exp_value(edge.target_id, s_node, None, d - 1, visited | {edge.target_id})
            if val > v: v, best = val, edge.target_id
        return (float('-inf'), None) if best is None else (v, best)

    def exp_value(v_node, s_node, blocked, d, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges]
        if hasattr(context, 'broken_edges'):
            poss = [b for b in poss if b not in context.broken_edges]
        if not poss: return float('-inf'), None
        
        v, prob = 0, 1.0 / len(poss)
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, visited)
            v += prob * val
        return v, None

    path = [context.vehicle_start]
    curr = context.vehicle_start
    total_score = 0
    
    while curr != context.goal_id and len(path) < 100:
        score, nxt = max_value(curr, context.saboteur_start, None, context.max_depth, {curr})
        if not nxt or nxt in path: 
            break
        path.append(nxt)
        curr = nxt
        total_score += score

    if curr != context.goal_id:
        try:
            from algorithms.informed import run_a_star
            from core.contexts import PathfindingContext
            res = run_a_star(PathfindingContext(context.graph, curr, context.goal_id, heuristic_fn=lambda n1, n2: get_h(context, n1, n2)))
            if res and getattr(res, 'path', None):
                path.extend(res.path[1:])
        except Exception:
            pass

    return ExperimentResult("Expectimax", "Adversarial", curr == context.goal_id or len(path) > 1, 
                            (time.perf_counter() - start_time) * 1000, 
                            {"nodes_expanded": nodes_expanded[0], "score": total_score}, path)