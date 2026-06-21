import time
from collections import deque
from core.metrics import ExperimentResult

def run_bfs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph = context.graph
    start_id = context.start_id
    goal_id = context.goal_id

    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return ExperimentResult("BFS", "Uninformed", False, 0.0)

    queue = deque([start_id])
    came_from = {start_id: None}
    nodes_expanded = 0

    while queue:
        curr_id = queue.popleft()
        nodes_expanded += 1

        if curr_id == goal_id:
            path = []
            while curr_id is not None:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            path.reverse()
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExperimentResult("BFS", "Uninformed", True, exec_time, {"nodes_expanded": nodes_expanded}, path)

        for edge in graph.nodes[curr_id].edges:
            neighbor_id = edge.target_id
            if neighbor_id not in came_from:
                came_from[neighbor_id] = curr_id
                queue.append(neighbor_id)

    exec_time = (time.perf_counter() - start_time) * 1000
    return ExperimentResult("BFS", "Uninformed", False, exec_time, {"nodes_expanded": nodes_expanded})
