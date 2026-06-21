import time
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
