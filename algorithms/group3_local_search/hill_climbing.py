import time
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
