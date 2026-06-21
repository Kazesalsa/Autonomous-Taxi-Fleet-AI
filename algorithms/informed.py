import time
import heapq
from core.metrics import ExperimentResult

def run_gbfs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id, h_fn = context.graph, context.start_id, context.goal_id, context.heuristic_fn
    if start_id not in graph.nodes or goal_id not in graph.nodes or not h_fn:
        return ExperimentResult("Greedy Best-First", "Informed", False, 0.0)
    goal_node = graph.nodes[goal_id]
    open_set = []
    heapq.heappush(open_set, (h_fn(graph.nodes[start_id], goal_node), start_id))
    came_from = {start_id: None}
    nodes_expanded = 0
    while open_set:
        _, curr_id = heapq.heappop(open_set)
        nodes_expanded += 1
        if curr_id == goal_id:
            path = []
            while curr_id is not None:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            return ExperimentResult("Greedy Best-First", "Informed", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded}, path[::-1])
        for edge in graph.nodes[curr_id].edges:
            if edge.target_id not in came_from:
                came_from[edge.target_id] = curr_id
                heapq.heappush(open_set, (h_fn(graph.nodes[edge.target_id], goal_node), edge.target_id))
    return ExperimentResult("Greedy Best-First", "Informed", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded})

def run_a_star(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id, h_fn = context.graph, context.start_id, context.goal_id, context.heuristic_fn
    if start_id not in graph.nodes or goal_id not in graph.nodes or not h_fn:
        return ExperimentResult("A*", "Informed", False, 0.0)
    goal_node = graph.nodes[goal_id]
    open_set = []
    heapq.heappush(open_set, (h_fn(graph.nodes[start_id], goal_node), start_id))
    came_from = {start_id: None}
    g_score = {start_id: 0}
    nodes_expanded = 0
    while open_set:
        _, curr_id = heapq.heappop(open_set)
        nodes_expanded += 1
        if curr_id == goal_id:
            path = []
            while curr_id is not None:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            return ExperimentResult("A*", "Informed", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded, "cost": g_score[goal_id]}, path[::-1])
        for edge in graph.nodes[curr_id].edges:
            tentative_g = g_score[curr_id] + edge.get_weight()
            if tentative_g < g_score.get(edge.target_id, float('inf')):
                came_from[edge.target_id] = curr_id
                g_score[edge.target_id] = tentative_g
                heapq.heappush(open_set, (tentative_g + h_fn(graph.nodes[edge.target_id], goal_node), edge.target_id))
    return ExperimentResult("A*", "Informed", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded})

def run_weighted_a_star(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id, h_fn, w = context.graph, context.start_id, context.goal_id, context.heuristic_fn, context.weight
    if start_id not in graph.nodes or goal_id not in graph.nodes or not h_fn:
        return ExperimentResult("Weighted A*", "Informed", False, 0.0)
    goal_node = graph.nodes[goal_id]
    open_set = []
    heapq.heappush(open_set, (h_fn(graph.nodes[start_id], goal_node) * w, start_id))
    came_from = {start_id: None}
    g_score = {start_id: 0}
    nodes_expanded = 0
    while open_set:
        _, curr_id = heapq.heappop(open_set)
        nodes_expanded += 1
        if curr_id == goal_id:
            path = []
            while curr_id is not None:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            return ExperimentResult("Weighted A*", "Informed", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded, "cost": g_score[goal_id]}, path[::-1])
        for edge in graph.nodes[curr_id].edges:
            tentative_g = g_score[curr_id] + edge.get_weight()
            if tentative_g < g_score.get(edge.target_id, float('inf')):
                came_from[edge.target_id] = curr_id
                g_score[edge.target_id] = tentative_g
                heapq.heappush(open_set, (tentative_g + (h_fn(graph.nodes[edge.target_id], goal_node) * w), edge.target_id))
    return ExperimentResult("Weighted A*", "Informed", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded})
