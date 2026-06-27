import time
import random
from collections import deque
from core.metrics import ExperimentResult

def run_backtracking(context) -> ExperimentResult:
    start_time = time.perf_counter()
    assignment, steps = {}, [0]
    def backtrack(assign):
        if len(assign) == len(context.variables): return assign
        var = [v for v in context.variables if v not in assign][0]
        for value in context.domains[var]:
            steps[0] += 1
            consistent = True
            for n in context.neighbors[var]:
                if n in assign and not context.constraints(var, value, n, assign[n]):
                    consistent = False
                    break
            if consistent:
                assign[var] = value
                res = backtrack(assign)
                if res: return res
                del assign[var]
        return None
    res = backtrack(assignment)
    return ExperimentResult("Backtracking", "CSP", res is not None, (time.perf_counter() - start_time) * 1000, {"steps": steps[0], "violations": 0 if res else -1}, res)

def run_ac3(context) -> ExperimentResult:
    start_time = time.perf_counter()
    domains = {v: list(context.domains[v]) for v in context.variables}
    queue = deque([(v, n) for v in context.variables for n in context.neighbors[v]])
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
                return ExperimentResult("AC-3", "CSP", False, (time.perf_counter() - start_time) * 1000, {"steps": steps}, None)
            for xk in context.neighbors[xi]:
                if xk != xj: queue.append((xk, xi))
    def backtrack(assign):
        if len(assign) == len(context.variables): return assign
        var = [v for v in context.variables if v not in assign][0]
        for value in domains[var]:
            if all(context.constraints(var, value, n, assign[n]) for n in context.neighbors[var] if n in assign):
                assign[var] = value
                res = backtrack(assign)
                if res: return res
                del assign[var]
        return None
    res = backtrack({})
    return ExperimentResult("AC-3", "CSP", res is not None, (time.perf_counter() - start_time) * 1000, {"steps": steps}, res)

def run_min_conflicts(context) -> ExperimentResult:
    start_time = time.perf_counter()
    if not context.variables:
         return ExperimentResult("Min-Conflicts", "CSP", False, 0.0, {"steps": 0, "violations": 0}, None)
    for v in context.variables:
        if not context.domains[v]:
            return ExperimentResult("Min-Conflicts", "CSP", False, 0.0, {"steps": 0, "violations": 0}, None)
    current = {v: random.choice(context.domains[v]) for v in context.variables}
    def get_conflicts(var, val, assign):
        return sum(1 for n in context.neighbors[var] if not context.constraints(var, val, n, assign[n]))
    steps = 0
    while steps < context.max_steps:
        conflicted = [v for v in context.variables if get_conflicts(v, current[v], current) > 0]
        if not conflicted:
            return ExperimentResult("Min-Conflicts", "CSP", True, (time.perf_counter() - start_time) * 1000, {"steps": steps, "violations": 0}, current)
        var = random.choice(conflicted)
        min_c, best_vals = float('inf'), []
        for val in context.domains[var]:
            c = get_conflicts(var, val, current)
            if c < min_c:
                min_c, best_vals = c, [val]
            elif c == min_c:
                best_vals.append(val)
        current[var] = random.choice(best_vals)
        steps += 1
    violations = sum(1 for v in context.variables if get_conflicts(v, current[v], current) > 0)
    return ExperimentResult("Min-Conflicts", "CSP", False, (time.perf_counter() - start_time) * 1000, {"steps": steps, "violations": violations}, current)


class TaxiCSPContext:
    def __init__(self, customers, taxis, graph):
        self.variables = []
        self.domains = {}
        for c in customers:
            self.variables.append(c['label'])
            self.domains[c['label']] = list(taxis)
        self.neighbors = {v: [n for n in self.variables if n != v] for v in self.variables}
        self.max_steps = 100

    def constraints(self, var1, val1, var2, val2):
        # AllDiff constraint: a taxi can only be assigned to one customer
        return val1 != val2

def solve_taxi_assignment_backtracking(customers, taxis, graph):
    if not customers or not taxis: return {}
    ctx = TaxiCSPContext(customers, taxis, graph)
    if not ctx.variables: return {}
    res = run_backtracking(ctx)
    return res.path if res and res.path else {}

def solve_taxi_assignment_minconflicts(customers, taxis, graph):
    if not customers or not taxis: return {}
    ctx = TaxiCSPContext(customers, taxis, graph)
    if not ctx.variables: return {}
    res = run_min_conflicts(ctx)
    return res.path if res and res.success and res.path else {}

class TrafficLightCSPContext:
    def __init__(self, target_groups, required_axes):
        self.variables = list(target_groups)
        self.domains = {v: ['H_GREEN', 'V_GREEN'] for v in self.variables}
        self.neighbors = {v: [n for n in self.variables if n != v] for v in self.variables}
        self.required_axes = required_axes

    def constraints(self, var1, val1, var2, val2):
        # Unary constraint: if var1 has a required axis, val1 must match it
        req1 = self.required_axes.get(var1)
        if req1 and val1 != f"{req1}_GREEN":
            return False
        
        req2 = self.required_axes.get(var2)
        if req2 and val2 != f"{req2}_GREEN":
            return False
            
        return True

def solve_traffic_light_ac3(target_groups, required_axes):
    if not target_groups: return {}
    ctx = TrafficLightCSPContext(target_groups, required_axes)
    res = run_ac3(ctx)
    return res.path if res and res.path else {}



