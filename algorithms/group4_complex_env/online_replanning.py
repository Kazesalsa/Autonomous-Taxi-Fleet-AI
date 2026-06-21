import time
import heapq
from core.metrics import ExperimentResult

def a_star(graph, start_id, goal_id, h_fn, known_broken):
    open_set = []
    heapq.heappush(open_set, (0, start_id))
    came_from = {start_id: None}
    g_score = {start_id: 0}
    
    while open_set:
        _, curr = heapq.heappop(open_set)
        if curr == goal_id:
            path = []
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            return path[::-1]
            
        for edge in graph.nodes[curr].edges:
            nxt = edge.target_id
            e_tuple = tuple(sorted((curr, nxt)))
            if e_tuple in known_broken: continue
            
            tentative_g = g_score[curr] + edge.get_weight()
            if tentative_g < g_score.get(nxt, float('inf')):
                came_from[nxt] = curr
                g_score[nxt] = tentative_g
                f = tentative_g + h_fn(graph.nodes[nxt], graph.nodes[goal_id])
                heapq.heappush(open_set, (f, nxt))
    return []

def run_online_replanning(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    curr = context.start_id
    goal = context.goal_id
    broken_edges = context.broken_edges
    
    known_broken = set()
    actual_path = [curr]
    replans = 0
    nodes_expanded = 0
    
    while curr != goal:
        plan = a_star(graph, curr, goal, context.heuristic_fn, known_broken)
        if not plan: break
            
        nxt = plan[1]
        e_tuple = tuple(sorted((curr, nxt)))
        nodes_expanded += len(plan)
        
        if e_tuple in broken_edges and broken_edges[e_tuple]['type'] != 'CROSSWALK':
            known_broken.add(e_tuple)
            replans += 1
        else:
            curr = nxt
            actual_path.append(curr)
            
    exec_time = (time.perf_counter() - start_time) * 1000
    success = (curr == goal)
    return ExperimentResult("Online Replanning", "Complex Env", success, exec_time, {"replans": replans, "nodes_expanded": nodes_expanded}, actual_path)
