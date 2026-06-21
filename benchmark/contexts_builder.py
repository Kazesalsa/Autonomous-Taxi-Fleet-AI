import math
from core.graph import Graph
from core.contexts import PathfindingContext, TrafficOptimizationContext, CSPContext, ComplexEnvContext, AdversarialContext

def heuristic(n1, n2): return math.hypot(n1.x - n2.x, n1.y - n2.y)

def get_benchmark_contexts():
    g = Graph()
    for i in range(5):
        for j in range(5): g.add_node(f'N_{i}_{j}', i*80 + 100, j*80 + 100)
    for i in range(5):
        for j in range(5):
            if i < 4: g.add_bidirectional_edge(f'N_{i}_{j}', f'N_{i+1}_{j}', 0.1)
            if j < 4: g.add_bidirectional_edge(f'N_{i}_{j}', f'N_{i}_{j+1}', 0.1)
    return {
        "Group 1: Uninformed": PathfindingContext(g, 'N_0_0', 'N_4_4'),
        "Group 2: Informed": PathfindingContext(g, 'N_0_0', 'N_4_4', heuristic_fn=heuristic),
        "Group 3: Local Search": TrafficOptimizationContext(g, ['N_1_1', 'N_2_2', 'N_3_3'], lambda s: sum(abs(v - 45) for v in s.values()), {'N_1_1': 30, 'N_2_2': 60, 'N_3_3': 90}),
        "Group 4: Complex Env": ComplexEnvContext(g, 'N_0_0', 'N_4_4', {tuple(sorted(('N_2_2', 'N_2_3'))): {'type': 'ROCK', 'discovered': False}}, heuristic),
        "Group 5: CSP": CSPContext(['L1', 'L2', 'L3', 'L4'], {v: [0, 15, 30, 45] for v in ['L1', 'L2', 'L3', 'L4']}, lambda v, x, n, y: x != y, {'L1': ['L2'], 'L2': ['L1', 'L3'], 'L3': ['L2', 'L4'], 'L4': ['L3']}),
        "Group 6: Adversarial": AdversarialContext(g, 'N_0_0', 'N_2_0', 'N_4_4', 4, heuristic)
    }
