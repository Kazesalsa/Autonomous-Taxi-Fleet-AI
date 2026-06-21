import time
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
