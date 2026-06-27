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
    
    from algorithms.informed import run_a_star
    from core.contexts import PathfindingContext
    
    # 1. Dùng A* tìm đường đi toàn cục (Global Path)
    a_star_ctx = PathfindingContext(context.graph, context.vehicle_start, context.goal_id)
    a_star_ctx.heuristic_fn = context.heuristic_fn if hasattr(context, 'heuristic_fn') else None
    a_star_res = run_a_star(a_star_ctx)
    global_path = a_star_res.path if a_star_res and hasattr(a_star_res, 'path') and a_star_res.path else []
    
    path_dist = {n: len(global_path) - 1 - i for i, n in enumerate(global_path)}
    
    def eval_fn(v): 
        if v in path_dist:
            base_h = -path_dist[v] * 100
        else:
            base_h = -get_h(context, context.graph.nodes[v], context.graph.nodes[context.goal_id]) - 5000
        return base_h - (100000 if v in visited_global else 0)
    
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
            if val > v or best is None: v, best = val, edge.target_id
        return (eval_fn(v_node), None) if best is None else (v, best)

    def min_value(v_node, s_node, blocked, d, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('inf'), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges if e.target_id != context.goal_id]
        if hasattr(context, 'broken_edges'):
            poss = [b for b in poss if b not in context.broken_edges]
        if not poss: poss = [None]
        
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, visited)
            if val < v or best is None: v, best = val, b
        return v, best

    path = [context.vehicle_start]
    curr = context.vehicle_start
    total_score = 0
    visited_global = {curr}

    while curr != context.goal_id and len(path) < 200:
        score, nxt = max_value(curr, context.saboteur_start, None, context.max_depth, {curr})
        if not nxt:
            break
        path.append(nxt)
        visited_global.add(nxt)
        curr = nxt
        total_score += score

    return ExperimentResult("Minimax", "Adversarial", curr == context.goal_id or len(path) > 1,
                            (time.perf_counter() - start_time) * 1000,
                            {"nodes_expanded": nodes_expanded[0], "score": total_score}, path)

def run_alpha_beta(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    
    from algorithms.informed import run_a_star
    from core.contexts import PathfindingContext
    
    # 1. Dùng A* tìm đường đi toàn cục (Global Path)
    a_star_ctx = PathfindingContext(context.graph, context.vehicle_start, context.goal_id)
    a_star_ctx.heuristic_fn = context.heuristic_fn if hasattr(context, 'heuristic_fn') else None
    a_star_res = run_a_star(a_star_ctx)
    global_path = a_star_res.path if a_star_res and hasattr(a_star_res, 'path') and a_star_res.path else []
    
    path_dist = {n: len(global_path) - 1 - i for i, n in enumerate(global_path)}
    
    def eval_fn(v): 
        if v in path_dist:
            base_h = -path_dist[v] * 100
        else:
            base_h = -get_h(context, context.graph.nodes[v], context.graph.nodes[context.goal_id]) - 5000
        return base_h - (100000 if v in visited_global else 0)
    
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
            if val > v or best is None: v, best = val, edge.target_id
            if v >= beta: return v, best
            alpha = max(alpha, v)
        return (eval_fn(v_node), None) if best is None else (v, best)

    def min_value(v_node, s_node, blocked, d, alpha, beta, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('inf'), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges if e.target_id != context.goal_id]
        if hasattr(context, 'broken_edges'):
            poss = [b for b in poss if b not in context.broken_edges]
        if not poss: poss = [None]
        
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, alpha, beta, visited)
            if val < v or best is None: v, best = val, b
            if v <= alpha: return v, best
            beta = min(beta, v)
        return v, best

    path = [context.vehicle_start]
    curr = context.vehicle_start
    total_score = 0
    visited_global = {curr}

    while curr != context.goal_id and len(path) < 200:
        score, nxt = max_value(curr, context.saboteur_start, None, context.max_depth, float('-inf'), float('inf'), {curr})
        if not nxt:
            break
        path.append(nxt)
        visited_global.add(nxt)
        curr = nxt
        total_score += score

    return ExperimentResult("Alpha-Beta", "Adversarial", curr == context.goal_id or len(path) > 1,
                            (time.perf_counter() - start_time) * 1000,
                            {"nodes_expanded": nodes_expanded[0], "score": total_score}, path)

def run_expectimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    
    from algorithms.informed import run_a_star
    from core.contexts import PathfindingContext
    
    # 1. Dùng A* tìm đường đi toàn cục (Global Path)
    a_star_ctx = PathfindingContext(context.graph, context.vehicle_start, context.goal_id)
    a_star_ctx.heuristic_fn = context.heuristic_fn if hasattr(context, 'heuristic_fn') else None
    a_star_res = run_a_star(a_star_ctx)
    global_path = a_star_res.path if a_star_res and hasattr(a_star_res, 'path') and a_star_res.path else []
    
    path_dist = {n: len(global_path) - 1 - i for i, n in enumerate(global_path)}
    
    def eval_fn(v): 
        if v in path_dist:
            base_h = -path_dist[v] * 100
        else:
            base_h = -get_h(context, context.graph.nodes[v], context.graph.nodes[context.goal_id]) - 5000
        return base_h - (100000 if v in visited_global else 0)
    
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
            if val > v or best is None: v, best = val, edge.target_id
        return (eval_fn(v_node), None) if best is None else (v, best)

    def exp_value(v_node, s_node, blocked, d, visited):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges if e.target_id != context.goal_id]
        if hasattr(context, 'broken_edges'):
            poss = [b for b in poss if b not in context.broken_edges]
        if not poss: poss = [None]
        
        v, prob = 0, 1.0 / len(poss)
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, visited)
            v += prob * val
        return v, None

    path = [context.vehicle_start]
    curr = context.vehicle_start
    total_score = 0
    visited_global = {curr}

    while curr != context.goal_id and len(path) < 200:
        score, nxt = max_value(curr, context.saboteur_start, None, context.max_depth, {curr})
        if not nxt:
            break
        path.append(nxt)
        visited_global.add(nxt)
        curr = nxt
        total_score += score

    return ExperimentResult("Expectimax", "Adversarial", curr == context.goal_id or len(path) > 1,
                            (time.perf_counter() - start_time) * 1000,
                            {"nodes_expanded": nodes_expanded[0], "score": total_score}, path)