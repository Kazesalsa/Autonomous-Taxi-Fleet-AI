import time
import random
import math
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
                new_dur = duration + delta
                if 10 <= new_dur <= 120:
                    neighbor = current_state.copy()
                    neighbor[node] = new_dur
                    score = context.objective_fn(neighbor)
                    if score < best_score:
                        best_score, best_neighbor = score, neighbor
        if best_neighbor is None or best_score >= current_score:
            break
        current_state, current_score = best_neighbor, best_score
        iterations += 1
    return ExperimentResult("Hill Climbing", "Local Search", True, (time.perf_counter() - start_time) * 1000, {"iterations": iterations, "final_score": current_score}, None)

def run_simulated_annealing(context) -> ExperimentResult:
    start_time = time.perf_counter()
    current_state = context.initial_state.copy()
    current_score = context.objective_fn(current_state)
    T, cooling_rate, iterations = 100.0, 0.95, 0
    best_state, best_score = current_state, current_score
    while iterations < context.max_iterations and T > 0.1:
        if not current_state: break
        node = random.choice(list(current_state.keys()))
        new_dur = current_state[node] + random.choice([-5, 5])
        if 10 <= new_dur <= 120:
            neighbor = current_state.copy()
            neighbor[node] = new_dur
            neighbor_score = context.objective_fn(neighbor)
            if neighbor_score < current_score or random.random() < math.exp((current_score - neighbor_score) / T):
                current_state, current_score = neighbor, neighbor_score
                if current_score < best_score:
                    best_score, best_state = current_score, current_state
        T *= cooling_rate
        iterations += 1
    return ExperimentResult("Simulated Annealing", "Local Search", True, (time.perf_counter() - start_time) * 1000, {"iterations": iterations, "final_score": best_score}, None)

def run_local_beam_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    k, states = context.k_beam, [context.initial_state.copy() for _ in range(context.k_beam)]
    iterations, best_score = 0, float('inf')
    while iterations < context.max_iterations:
        all_neighbors = []
        for state in states:
            all_neighbors.append((context.objective_fn(state), state))
            for node, duration in state.items():
                for delta in [-5, 5]:
                    if 10 <= duration + delta <= 120:
                        neighbor = state.copy()
                        neighbor[node] = duration + delta
                        all_neighbors.append((context.objective_fn(neighbor), neighbor))
        all_neighbors.sort(key=lambda x: x[0])
        next_states, seen = [], set()
        for score, state in all_neighbors:
            st = tuple(sorted(state.items()))
            if st not in seen:
                seen.add(st)
                next_states.append((score, state))
            if len(next_states) == k: break
        if not next_states: break
        states = [s[1] for s in next_states]
        if next_states[0][0] >= best_score: break
        best_score = next_states[0][0]
        iterations += 1
    return ExperimentResult("Local Beam Search", "Local Search", True, (time.perf_counter() - start_time) * 1000, {"iterations": iterations, "final_score": best_score}, None)
