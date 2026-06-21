from algorithms.group1_uninformed.bfs import run_bfs
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
