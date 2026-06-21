import os

def create_phase2_files():
    files = {
        "core/contexts.py": r"""from dataclasses import dataclass
from typing import Callable, Any, Optional, Dict, List

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
""",
        "algorithms/group3_local_search/__init__.py": "",
        "algorithms/group3_local_search/hill_climbing.py": r"""import time
from core.metrics import ExperimentResult

def run_hill_climbing(context) -> ExperimentResult:
    start_time = time.perf_counter()
    current_state = context.initial_state.copy()
    current_score = context.objective_fn(current_state)
    iterations = 0

    while iterations < context.max_iterations:
        best_neighbor = None
        best_score = float('inf')
        
        for node, duration in current_state.items():
            for delta in [-5, 5]:
                new_duration = duration + delta
                if 10 <= new_duration <= 120:
                    neighbor = current_state.copy()
                    neighbor[node] = new_duration
                    score = context.objective_fn(neighbor)
                    if score < best_score:
                        best_score = score
                        best_neighbor = neighbor
        
        if best_neighbor is None or best_score >= current_score:
            break
            
        current_state = best_neighbor
        current_score = best_score
        iterations += 1

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Hill Climbing", "Local Search", True, exec_time, 
                          {"iterations": iterations, "final_score": current_score}, None)
""",
        "algorithms/group3_local_search/simulated_annealing.py": r"""import time
import random
import math
from core.metrics import ExperimentResult

def run_simulated_annealing(context) -> ExperimentResult:
    start_time = time.perf_counter()
    current_state = context.initial_state.copy()
    current_score = context.objective_fn(current_state)
    
    T = 100.0
    cooling_rate = 0.95
    iterations = 0
    
    best_state = current_state
    best_score = current_score

    while iterations < context.max_iterations and T > 0.1:
        if not current_state:
            break
        node = random.choice(list(current_state.keys()))
        delta = random.choice([-5, 5])
        new_duration = current_state[node] + delta
        
        if 10 <= new_duration <= 120:
            neighbor = current_state.copy()
            neighbor[node] = new_duration
            neighbor_score = context.objective_fn(neighbor)
            
            if neighbor_score < current_score or random.random() < math.exp((current_score - neighbor_score) / T):
                current_state = neighbor
                current_score = neighbor_score
                if current_score < best_score:
                    best_score = current_score
                    best_state = current_state

        T *= cooling_rate
        iterations += 1

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Simulated Annealing", "Local Search", True, exec_time, 
                          {"iterations": iterations, "final_score": best_score}, None)
""",
        "algorithms/group3_local_search/local_beam_search.py": r"""import time
from core.metrics import ExperimentResult

def run_local_beam_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    k = context.k_beam
    
    states = [context.initial_state.copy() for _ in range(k)]
    iterations = 0
    best_score = float('inf')

    while iterations < context.max_iterations:
        all_neighbors = []
        for state in states:
            score = context.objective_fn(state)
            all_neighbors.append((score, state))
            
            for node, duration in state.items():
                for delta in [-5, 5]:
                    new_duration = duration + delta
                    if 10 <= new_duration <= 120:
                        neighbor = state.copy()
                        neighbor[node] = new_duration
                        n_score = context.objective_fn(neighbor)
                        all_neighbors.append((n_score, neighbor))
        
        all_neighbors.sort(key=lambda x: x[0])
        next_states = []
        seen = set()
        for score, state in all_neighbors:
            state_tuple = tuple(sorted(state.items()))
            if state_tuple not in seen:
                seen.add(state_tuple)
                next_states.append((score, state))
            if len(next_states) == k:
                break
                
        if not next_states:
            break
            
        states = [s[1] for s in next_states]
        current_best = next_states[0][0]
        
        if current_best >= best_score:
            break
        best_score = current_best
        iterations += 1

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Local Beam Search", "Local Search", True, exec_time, 
                          {"iterations": iterations, "final_score": best_score}, None)
""",
        "algorithms/group5_csp/__init__.py": "",
        "algorithms/group5_csp/backtracking.py": r"""import time
from core.metrics import ExperimentResult

def run_backtracking(context) -> ExperimentResult:
    start_time = time.perf_counter()
    assignment = {}
    steps = [0]
    
    def backtrack(assign):
        if len(assign) == len(context.variables):
            return assign
        
        unassigned = [v for v in context.variables if v not in assign]
        var = unassigned[0]
        
        for value in context.domains[var]:
            steps[0] += 1
            consistent = True
            for neighbor in context.neighbors[var]:
                if neighbor in assign:
                    if not context.constraints(var, value, neighbor, assign[neighbor]):
                        consistent = False
                        break
                        
            if consistent:
                assign[var] = value
                result = backtrack(assign)
                if result: return result
                del assign[var]
                
        return None

    result = backtrack(assignment)
    exec_time = (time.perf_counter() - start_time) * 1000
    
    return ExperimentResult(
        "Backtracking", "CSP", result is not None, exec_time,
        {"steps": steps[0], "violations": 0 if result else -1}, None
    )
""",
        "algorithms/group5_csp/ac3.py": r"""import time
from collections import deque
from core.metrics import ExperimentResult

def run_ac3(context) -> ExperimentResult:
    start_time = time.perf_counter()
    domains = {v: list(context.domains[v]) for v in context.variables}
    queue = deque()
    for v in context.variables:
        for neighbor in context.neighbors[v]:
            queue.append((v, neighbor))
    
    steps = 0
    while queue:
        steps += 1
        xi, xj = queue.popleft()
        
        revised = False
        for x in domains[xi][:]:
            if not any(context.constraints(xi, x, xj, y) for y in domains[xj]):
                domains[xi].remove(x)
                revised = True
                
        if revised:
            if not domains[xi]:
                exec_time = (time.perf_counter() - start_time) * 1000
                return ExperimentResult("AC-3", "CSP", False, exec_time, {"steps": steps}, None)
            for xk in context.neighbors[xi]:
                if xk != xj:
                    queue.append((xk, xi))
                    
    assignment = {}
    def backtrack(assign):
        if len(assign) == len(context.variables): return assign
        var = [v for v in context.variables if v not in assign][0]
        for value in domains[var]:
            consistent = all(context.constraints(var, value, n, assign[n]) 
                           for n in context.neighbors[var] if n in assign)
            if consistent:
                assign[var] = value
                res = backtrack(assign)
                if res: return res
                del assign[var]
        return None
        
    res = backtrack(assignment)
    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("AC-3", "CSP", res is not None, exec_time, {"steps": steps}, None)
""",
        "algorithms/group5_csp/min_conflicts.py": r"""import time
import random
from core.metrics import ExperimentResult

def run_min_conflicts(context) -> ExperimentResult:
    start_time = time.perf_counter()
    
    if not context.variables:
         return ExperimentResult("Min-Conflicts", "CSP", False, 0.0, {"steps": 0, "violations": 0}, None)
         
    current = {v: random.choice(context.domains[v]) for v in context.variables}
    
    def get_conflicts(var, val, assign):
        count = 0
        for n in context.neighbors[var]:
            if not context.constraints(var, val, n, assign[n]):
                count += 1
        return count

    steps = 0
    while steps < context.max_steps:
        conflicted_vars = [v for v in context.variables if get_conflicts(v, current[v], current) > 0]
                
        if not conflicted_vars:
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExperimentResult("Min-Conflicts", "CSP", True, exec_time, {"steps": steps, "violations": 0}, None)
            
        var = random.choice(conflicted_vars)
        min_c = float('inf')
        best_vals = []
        for val in context.domains[var]:
            c = get_conflicts(var, val, current)
            if c < min_c:
                min_c = c
                best_vals = [val]
            elif c == min_c:
                best_vals.append(val)
                
        current[var] = random.choice(best_vals)
        steps += 1
        
    exec_time = (time.perf_counter() - start_time) * 1000
    violations = sum(1 for v in context.variables if get_conflicts(v, current[v], current) > 0)
    return ExperimentResult("Min-Conflicts", "CSP", False, exec_time, {"steps": steps, "violations": violations}, None)
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
    "Backtracking": run_backtracking,
    "AC-3": run_ac3,
    "Min-Conflicts": run_min_conflicts
}

GROUP_MAPPING = {
    "Group 1: Uninformed": ["BFS", "DFS", "UCS"],
    "Group 2: Informed": ["GBFS", "A*", "Weighted A*"],
    "Group 3: Local Search": ["Hill Climbing", "Simulated Annealing", "Local Beam Search"],
    "Group 5: CSP": ["Backtracking", "AC-3", "Min-Conflicts"]
}
"""
    }

    for path, content in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_phase2_files()