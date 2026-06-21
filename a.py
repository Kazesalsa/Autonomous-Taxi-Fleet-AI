import os

def create_phase4_files():
    files = {
        "core/contexts.py": r"""from dataclasses import dataclass
from typing import Callable, Any, Optional, Dict, List, Set, Tuple

@dataclass
class PathfindingContext:
    graph: Any
    start_id: str
    goal_id: str
    heuristic_fn: Optional[Callable[[Any, Any], float]] = None
    weight: float = 1.0

@dataclass
class TrafficOptimizationContext:
    graph: Any
    light_nodes: List[str]
    objective_fn: Callable[[Dict[str, int]], float]
    initial_state: Dict[str, int]
    max_iterations: int = 1000
    k_beam: int = 3

@dataclass
class CSPContext:
    variables: List[str]
    domains: Dict[str, List[int]]
    constraints: Callable[[str, int, str, int], bool]
    neighbors: Dict[str, List[str]]
    max_steps: int = 1000

@dataclass
class ComplexEnvContext:
    graph: Any
    start_id: str
    goal_id: str
    broken_edges: Dict[Tuple[str, str], Dict[str, Any]]
    heuristic_fn: Callable[[Any, Any], float]
    sensor_range: float = 150.0

@dataclass
class AdversarialContext:
    graph: Any
    vehicle_start: str
    saboteur_start: str
    goal_id: str
    max_depth: int = 4
    heuristic_fn: Optional[Callable[[Any, Any], float]] = None
""",
        "algorithms/group6_adversarial/__init__.py": "",
        "algorithms/group6_adversarial/minimax.py": r"""import time
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
""",
        "algorithms/group6_adversarial/alpha_beta.py": r"""import time
from core.metrics import ExperimentResult

def run_alpha_beta(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    goal = context.goal_id
    h_fn = context.heuristic_fn
    
    nodes_expanded = [0]
    
    def terminal_test(v_node, depth): return v_node == goal or depth == 0
    def eval_fn(v_node): return -h_fn(graph.nodes[v_node], graph.nodes[goal])

    def max_value(v_node, s_node, blocked_edge, depth, alpha, beta):
        nodes_expanded[0] += 1
        if terminal_test(v_node, depth): return eval_fn(v_node), None
        v = float('-inf')
        best_action = None
        for edge in graph.nodes[v_node].edges:
            nxt = edge.target_id
            if tuple(sorted((v_node, nxt))) == blocked_edge: continue
            val, _ = min_value(nxt, s_node, None, depth - 1, alpha, beta)
            if val > v:
                v = val; best_action = nxt
            if v >= beta: return v, best_action
            alpha = max(alpha, v)
        if best_action is None: return eval_fn(v_node), None
        return v, best_action

    def min_value(v_node, s_node, blocked_edge, depth, alpha, beta):
        nodes_expanded[0] += 1
        if terminal_test(v_node, depth): return eval_fn(v_node), None
        v = float('inf')
        best_action = None
        possible_blocks = [tuple(sorted((v_node, e.target_id))) for e in graph.nodes[v_node].edges]
        if not possible_blocks: possible_blocks = [None]
        
        for block in possible_blocks:
            val, _ = max_value(v_node, s_node, block, depth - 1, alpha, beta)
            if val < v:
                v = val; best_action = block
            if v <= alpha: return v, best_action
            beta = min(beta, v)
        return v, best_action

    score, next_move = max_value(context.vehicle_start, context.saboteur_start, None, context.max_depth, float('-inf'), float('inf'))
    
    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Alpha-Beta", "Adversarial", next_move is not None, exec_time, {"nodes_expanded": nodes_expanded[0], "score": score}, [context.vehicle_start, next_move] if next_move else [])
""",
        "algorithms/group6_adversarial/expectimax.py": r"""import time
from core.metrics import ExperimentResult

def run_expectimax(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    goal = context.goal_id
    h_fn = context.heuristic_fn
    
    nodes_expanded = [0]
    
    def terminal_test(v_node, depth): return v_node == goal or depth == 0
    def eval_fn(v_node): return -h_fn(graph.nodes[v_node], graph.nodes[goal])

    def max_value(v_node, s_node, blocked_edge, depth):
        nodes_expanded[0] += 1
        if terminal_test(v_node, depth): return eval_fn(v_node), None
        v = float('-inf')
        best_action = None
        for edge in graph.nodes[v_node].edges:
            nxt = edge.target_id
            if tuple(sorted((v_node, nxt))) == blocked_edge: continue
            val, _ = exp_value(nxt, s_node, None, depth - 1)
            if val > v:
                v = val; best_action = nxt
        if best_action is None: return eval_fn(v_node), None
        return v, best_action

    def exp_value(v_node, s_node, blocked_edge, depth):
        nodes_expanded[0] += 1
        if terminal_test(v_node, depth): return eval_fn(v_node), None
        possible_blocks = [tuple(sorted((v_node, e.target_id))) for e in graph.nodes[v_node].edges]
        if not possible_blocks: return eval_fn(v_node), None
        
        v = 0
        prob = 1.0 / len(possible_blocks)
        for block in possible_blocks:
            val, _ = max_value(v_node, s_node, block, depth - 1)
            v += prob * val
        return v, None

    score, next_move = max_value(context.vehicle_start, context.saboteur_start, None, context.max_depth)
    
    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Expectimax", "Adversarial", next_move is not None, exec_time, {"nodes_expanded": nodes_expanded[0], "score": score}, [context.vehicle_start, next_move] if next_move else [])
""",
        "algorithms/registry.py": r"""from algorithms.group1_uninformed.bfs import run_bfs
from algorithms.group1_uninformed.dfs import run_dfs
from algorithms.group1_uninformed.ucs import run_ucs
from algorithms.group2_informed.greedy_best_first import run_gbfs
from algorithms.group2_informed.a_star import run_a_star
from algorithms.group2_informed.weighted_a_star import run_weighted_a_star
from algorithms.group3_local_search.hill_climbing import run_hill_climbing
from algorithms.group3_local_search.simulated_annealing import run_simulated_annealing
from algorithms.group3_local_search.local_beam_search import run_local_beam_search
from algorithms.group4_complex_env.and_or_search import run_and_or_search
from algorithms.group4_complex_env.online_replanning import run_online_replanning
from algorithms.group4_complex_env.sensorless_search import run_sensorless_search
from algorithms.group5_csp.backtracking import run_backtracking
from algorithms.group5_csp.ac3 import run_ac3
from algorithms.group5_csp.min_conflicts import run_min_conflicts
from algorithms.group6_adversarial.minimax import run_minimax
from algorithms.group6_adversarial.alpha_beta import run_alpha_beta
from algorithms.group6_adversarial.expectimax import run_expectimax

ALGORITHM_REGISTRY = {
    "BFS": run_bfs,
    "DFS": run_dfs,
    "UCS": run_ucs,
    "GBFS": run_gbfs,
    "A*": run_a_star,
    "Weighted A*": run_weighted_a_star,
    "Hill Climbing": run_hill_climbing,
    "Simulated Annealing": run_simulated_annealing,
    "Local Beam Search": run_local_beam_search,
    "AND-OR Search": run_and_or_search,
    "Online Replanning": run_online_replanning,
    "Sensorless Search": run_sensorless_search,
    "Backtracking": run_backtracking,
    "AC-3": run_ac3,
    "Min-Conflicts": run_min_conflicts,
    "Minimax": run_minimax,
    "Alpha-Beta": run_alpha_beta,
    "Expectimax": run_expectimax
}

GROUP_MAPPING = {
    "Group 1: Uninformed": ["BFS", "DFS", "UCS"],
    "Group 2: Informed": ["GBFS", "A*", "Weighted A*"],
    "Group 3: Local Search": ["Hill Climbing", "Simulated Annealing", "Local Beam Search"],
    "Group 4: Complex Env": ["AND-OR Search", "Online Replanning", "Sensorless Search"],
    "Group 5: CSP": ["Backtracking", "AC-3", "Min-Conflicts"],
    "Group 6: Adversarial": ["Minimax", "Alpha-Beta", "Expectimax"]
}
"""
    }

    for path, content in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_phase4_files()