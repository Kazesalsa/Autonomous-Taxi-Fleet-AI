import os

def create_phase3_files():
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
""",
        "algorithms/group4_complex_env/__init__.py": "",
        "algorithms/group4_complex_env/and_or_search.py": r"""import time
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
""",
        "algorithms/group4_complex_env/online_replanning.py": r"""import time
import heapq
from core.metrics import ExperimentResult

def a_star(graph, start_id, goal_id, h_fn, known_broken):
    open_set = []
    heapq.heappush(open_set, (0, start_id))
    came_from = {start_id: None}
    g_score = {start_id: 0}
    
    while open_set:
        _, curr = heapq.heappop(open_set)
        if curr == goal_id:
            path = []
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            return path[::-1]
            
        for edge in graph.nodes[curr].edges:
            nxt = edge.target_id
            e_tuple = tuple(sorted((curr, nxt)))
            if e_tuple in known_broken: continue
            
            tentative_g = g_score[curr] + edge.get_weight()
            if tentative_g < g_score.get(nxt, float('inf')):
                came_from[nxt] = curr
                g_score[nxt] = tentative_g
                f = tentative_g + h_fn(graph.nodes[nxt], graph.nodes[goal_id])
                heapq.heappush(open_set, (f, nxt))
    return []

def run_online_replanning(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    curr = context.start_id
    goal = context.goal_id
    broken_edges = context.broken_edges
    
    known_broken = set()
    actual_path = [curr]
    replans = 0
    nodes_expanded = 0
    
    while curr != goal:
        plan = a_star(graph, curr, goal, context.heuristic_fn, known_broken)
        if not plan: break
            
        nxt = plan[1]
        e_tuple = tuple(sorted((curr, nxt)))
        nodes_expanded += len(plan)
        
        if e_tuple in broken_edges and broken_edges[e_tuple]['type'] != 'CROSSWALK':
            known_broken.add(e_tuple)
            replans += 1
        else:
            curr = nxt
            actual_path.append(curr)
            
    exec_time = (time.perf_counter() - start_time) * 1000
    success = (curr == goal)
    return ExperimentResult("Online Replanning", "Complex Env", success, exec_time, {"replans": replans, "nodes_expanded": nodes_expanded}, actual_path)
""",
        "algorithms/group4_complex_env/sensorless_search.py": r"""import time
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
    "Min-Conflicts": run_min_conflicts
}

GROUP_MAPPING = {
    "Group 1: Uninformed": ["BFS", "DFS", "UCS"],
    "Group 2: Informed": ["GBFS", "A*", "Weighted A*"],
    "Group 3: Local Search": ["Hill Climbing", "Simulated Annealing", "Local Beam Search"],
    "Group 4: Complex Env": ["AND-OR Search", "Online Replanning", "Sensorless Search"],
    "Group 5: CSP": ["Backtracking", "AC-3", "Min-Conflicts"]
}
"""
    }

    for path, content in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_phase3_files()