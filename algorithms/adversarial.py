import time
from core.metrics import ExperimentResult

def run_minimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    def eval_fn(v): return -context.heuristic_fn(context.graph.nodes[v], context.graph.nodes[context.goal_id])
    def max_value(v_node, s_node, blocked, d):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('-inf'), None
        for edge in context.graph.nodes[v_node].edges:
            if tuple(sorted((v_node, edge.target_id))) == blocked: continue
            val, _ = min_value(edge.target_id, s_node, None, d - 1)
            if val > v: v, best = val, edge.target_id
        return (eval_fn(v_node), None) if best is None else (v, best)
    def min_value(v_node, s_node, blocked, d):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('inf'), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges] or [None]
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1)
            if val < v: v, best = val, b
        return v, best
    score, nxt = max_value(context.vehicle_start, context.saboteur_start, None, context.max_depth)
    return ExperimentResult("Minimax", "Adversarial", nxt is not None, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded[0], "score": score}, [context.vehicle_start, nxt] if nxt else [])

def run_alpha_beta(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    def eval_fn(v): return -context.heuristic_fn(context.graph.nodes[v], context.graph.nodes[context.goal_id])
    def max_value(v_node, s_node, blocked, d, alpha, beta):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('-inf'), None
        for edge in context.graph.nodes[v_node].edges:
            if tuple(sorted((v_node, edge.target_id))) == blocked: continue
            val, _ = min_value(edge.target_id, s_node, None, d - 1, alpha, beta)
            if val > v: v, best = val, edge.target_id
            if v >= beta: return v, best
            alpha = max(alpha, v)
        return (eval_fn(v_node), None) if best is None else (v, best)
    def min_value(v_node, s_node, blocked, d, alpha, beta):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('inf'), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges] or [None]
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1, alpha, beta)
            if val < v: v, best = val, b
            if v <= alpha: return v, best
            beta = min(beta, v)
        return v, best
    score, nxt = max_value(context.vehicle_start, context.saboteur_start, None, context.max_depth, float('-inf'), float('inf'))
    return ExperimentResult("Alpha-Beta", "Adversarial", nxt is not None, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded[0], "score": score}, [context.vehicle_start, nxt] if nxt else [])

def run_expectimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    def eval_fn(v): return -context.heuristic_fn(context.graph.nodes[v], context.graph.nodes[context.goal_id])
    def max_value(v_node, s_node, blocked, d):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        v, best = float('-inf'), None
        for edge in context.graph.nodes[v_node].edges:
            if tuple(sorted((v_node, edge.target_id))) == blocked: continue
            val, _ = exp_value(edge.target_id, s_node, None, d - 1)
            if val > v: v, best = val, edge.target_id
        return (eval_fn(v_node), None) if best is None else (v, best)
    def exp_value(v_node, s_node, blocked, d):
        nodes_expanded[0] += 1
        if v_node == context.goal_id or d == 0: return eval_fn(v_node), None
        poss = [tuple(sorted((v_node, e.target_id))) for e in context.graph.nodes[v_node].edges]
        if not poss: return eval_fn(v_node), None
        v, prob = 0, 1.0 / len(poss)
        for b in poss:
            val, _ = max_value(v_node, s_node, b, d - 1)
            v += prob * val
        return v, None
    score, nxt = max_value(context.vehicle_start, context.saboteur_start, None, context.max_depth)
    return ExperimentResult("Expectimax", "Adversarial", nxt is not None, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded[0], "score": score}, [context.vehicle_start, nxt] if nxt else [])
