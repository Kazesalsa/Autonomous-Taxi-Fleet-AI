import time
import heapq
from core.metrics import ExperimentResult

def run_ucs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    start_id = context.start_id
    goal_id = context.goal_id

    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return ExperimentResult("UCS", "Uninformed", False, 0.0)

    open_set = []
    heapq.heappush(open_set, (0, start_id))
    came_from = {start_id: None}
    cost_so_far = {start_id: 0}
    nodes_expanded = 0

    while open_set:
        current_cost, curr_id = heapq.heappop(open_set)
        nodes_expanded += 1

        if curr_id == goal_id:
            path = []
            while curr_id is not None:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            path.reverse()
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExperimentResult("UCS", "Uninformed", True, exec_time, {"nodes_expanded": nodes_expanded, "cost": current_cost}, path)

        if current_cost > cost_so_far.get(curr_id, float('inf')):
            continue

        for edge in graph.nodes[curr_id].edges:
            neighbor_id = edge.target_id
            new_cost = cost_so_far[curr_id] + edge.get_weight()
            
            if new_cost < cost_so_far.get(neighbor_id, float('inf')):
                cost_so_far[neighbor_id] = new_cost
                came_from[neighbor_id] = curr_id
                heapq.heappush(open_set, (new_cost, neighbor_id))

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("UCS", "Uninformed", False, exec_time, {"nodes_expanded": nodes_expanded})
