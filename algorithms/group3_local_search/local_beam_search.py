import time
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
