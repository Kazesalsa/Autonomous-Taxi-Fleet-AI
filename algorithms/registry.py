from algorithms.uninformed import run_bfs, run_dfs, run_ucs
from algorithms.informed import run_gbfs, run_a_star, run_weighted_a_star
from algorithms.local_search import run_hill_climbing, run_simulated_annealing, run_local_beam_search
from algorithms.complex_env import run_and_or_search, run_online_replanning, run_sensorless_search
from algorithms.csp import run_backtracking, run_ac3, run_min_conflicts
from algorithms.adversarial import run_minimax, run_alpha_beta, run_expectimax

ALGORITHM_REGISTRY = {
    "BFS": run_bfs, "DFS": run_dfs, "UCS": run_ucs,
    "GBFS": run_gbfs, "A*": run_a_star, "Weighted A*": run_weighted_a_star,
    "Hill Climbing": run_hill_climbing, "Simulated Annealing": run_simulated_annealing, "Local Beam Search": run_local_beam_search,
    "AND-OR Search": run_and_or_search, "Online Replanning": run_online_replanning, "Sensorless Search": run_sensorless_search,
    "Backtracking": run_backtracking, "AC-3": run_ac3, "Min-Conflicts": run_min_conflicts,
    "Minimax": run_minimax, "Alpha-Beta": run_alpha_beta, "Expectimax": run_expectimax
}

GROUP_MAPPING = {
    "Group 1: Uninformed": ["BFS", "DFS", "UCS"],
    "Group 2: Informed": ["GBFS", "A*", "Weighted A*"],
    "Group 3: Local Search": ["Hill Climbing", "Simulated Annealing", "Local Beam Search"],
    "Group 4: Complex Env": ["AND-OR Search", "Online Replanning", "Sensorless Search"],
    "Group 5: CSP": ["Backtracking", "AC-3", "Min-Conflicts"],
    "Group 6: Adversarial": ["Minimax", "Alpha-Beta", "Expectimax"]
}
