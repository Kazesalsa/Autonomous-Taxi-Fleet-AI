import time
import heapq
from core.metrics import ExperimentResult

def run_a_star(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    start_id = context.start_id
    goal_id = context.goal_id
    h_fn = context.heuristic_fn

    if start_id not in graph.nodes or goal_id not in graph.nodes or not h_fn:
        return ExperimentResult("A*", "Informed", False, 0.0)

    goal_node = graph.nodes[goal_id]
    open_set = []
    start_h = h_fn(graph.nodes[start_id], goal_node)
    heapq.heappush(open_set, (start_h, start_id))
    
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
            path.reverse()
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExperimentResult("A*", "Informed", True, exec_time, {"nodes_expanded": nodes_expanded, "cost": g_score[goal_id]}, path)

        for edge in graph.nodes[curr_id].edges:
            neighbor_id = edge.target_id
            tentative_g = g_score[curr_id] + edge.get_weight()

            if tentative_g < g_score.get(neighbor_id, float('inf')):
                came_from[neighbor_id] = curr_id
                g_score[neighbor_id] = tentative_g
                f_score = tentative_g + h_fn(graph.nodes[neighbor_id], goal_node)
                heapq.heappush(open_set, (f_score, neighbor_id))

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("A*", "Informed", False, exec_time, {"nodes_expanded": nodes_expanded})
