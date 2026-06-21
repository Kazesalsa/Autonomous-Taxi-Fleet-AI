import time
import heapq
from collections import deque
from core.metrics import ExperimentResult

def run_bfs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id = context.graph, context.start_id, context.goal_id
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
            return ExperimentResult("BFS", "Uninformed", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded}, path[::-1])
        for edge in graph.nodes[curr_id].edges:
            if edge.target_id not in came_from:
                came_from[edge.target_id] = curr_id
                queue.append(edge.target_id)
    return ExperimentResult("BFS", "Uninformed", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded})

def run_dfs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id = context.graph, context.start_id, context.goal_id
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return ExperimentResult("DFS", "Uninformed", False, 0.0)
    stack = [start_id]
    came_from = {start_id: None}
    nodes_expanded = 0
    while stack:
        curr_id = stack.pop()
        nodes_expanded += 1
        if curr_id == goal_id:
            path = []
            while curr_id is not None:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            return ExperimentResult("DFS", "Uninformed", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded}, path[::-1])
        for edge in reversed(graph.nodes[curr_id].edges):
            if edge.target_id not in came_from:
                came_from[edge.target_id] = curr_id
                stack.append(edge.target_id)
    return ExperimentResult("DFS", "Uninformed", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded})

def run_ucs(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id = context.graph, context.start_id, context.goal_id
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
            return ExperimentResult("UCS", "Uninformed", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded, "cost": current_cost}, path[::-1])
        if current_cost > cost_so_far.get(curr_id, float('inf')):
            continue
        for edge in graph.nodes[curr_id].edges:
            new_cost = cost_so_far[curr_id] + edge.get_weight()
            if new_cost < cost_so_far.get(edge.target_id, float('inf')):
                cost_so_far[edge.target_id] = new_cost
                came_from[edge.target_id] = curr_id
                heapq.heappush(open_set, (new_cost, edge.target_id))
    return ExperimentResult("UCS", "Uninformed", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded})
