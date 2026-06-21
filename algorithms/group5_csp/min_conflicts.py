import time
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
