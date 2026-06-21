import time
import heapq
from core.metrics import ExperimentResult

def run_gbfs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    start_id = context.start_id
    goal_id = context.goal_id
    h_fn = context.heuristic_fn

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
            path.reverse()
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExperimentResult("Greedy Best-First", "Informed", True, exec_time, {"nodes_expanded": nodes_expanded}, path)

        for edge in graph.nodes[curr_id].edges:
            neighbor_id = edge.target_id
            if neighbor_id not in came_from:
                came_from[neighbor_id] = curr_id
                h_val = h_fn(graph.nodes[neighbor_id], goal_node)
                heapq.heappush(open_set, (h_val, neighbor_id))

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("Greedy Best-First", "Informed", False, exec_time, {"nodes_expanded": nodes_expanded})
