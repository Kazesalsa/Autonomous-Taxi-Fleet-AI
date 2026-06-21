import time
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
