import math
import heapq
import random
from collections import deque

def v2v_rescue_bfs(graph, start_id, broken_edges_set):
    visited = {start_id}
    queue = deque([start_id])
    network = [start_id]
    while queue:
        curr = queue.popleft()
        for edge in graph.nodes[curr].edges:
            edge_id = tuple(sorted((curr, edge.target_id)))
            if edge_id not in broken_edges_set and edge.target_id not in visited:
                visited.add(edge.target_id)
                queue.append(edge.target_id)
                network.append(edge.target_id)
    return network

def bfs_find_nearest_taxi(graph, start_id, vehicles):
    visited = {start_id}
    queue = deque([start_id])
    while queue:
        curr_id = queue.popleft()
        for v in vehicles:
            if v.status in ["IDLE", "RETURNING"] and (v.current_node_id == curr_id or v.target_node_id == curr_id):
                return v
        for edge in graph.nodes[curr_id].edges:
            if edge.target_id not in visited:
                visited.add(edge.target_id)
                queue.append(edge.target_id)
    return None

def heuristic(n1, n2): return math.hypot(n1.x - n2.x, n1.y - n2.y)

def dynamic_routing_a_star(graph, start_id, goal_id, ignore_traffic=False, broken_edges_set=None):
    if start_id not in graph.nodes or goal_id not in graph.nodes: return []
    start = graph.nodes[start_id]
    goal = graph.nodes[goal_id]
    open_set = []
    heapq.heappush(open_set, (0, start_id))
    came_from = {}
    g_score = {start_id: 0}
    f_score = {start_id: heuristic(start, goal)}

    while open_set:
        _, curr_id = heapq.heappop(open_set)
        if curr_id == goal_id:
            path = []
            while curr_id in came_from:
                path.append(curr_id)
                curr_id = came_from[curr_id]
            path.append(start_id)
            return path[::-1]

        for edge in graph.nodes[curr_id].edges:
            neighbor_id = edge.target_id
            edge_id = tuple(sorted((curr_id, neighbor_id)))
            if broken_edges_set and edge_id in broken_edges_set: continue 
            weight = edge.distance if ignore_traffic else edge.get_weight()
            if weight == float('inf') and not ignore_traffic: continue
                
            tentative_g = g_score[curr_id] + weight
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = curr_id
                g_score[neighbor_id] = tentative_g
                f_score[neighbor_id] = tentative_g + heuristic(graph.nodes[neighbor_id], goal)
                heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
    return []

def online_search_replanning(graph, current_node, target_node, final_goal, broken_edges_set):
    start_re = target_node if target_node else current_node
    return dynamic_routing_a_star(graph, start_re, final_goal, broken_edges_set=broken_edges_set)

def optimize_traffic_lights_sa(graph, enabled=True):
    for node_id, node in graph.nodes.items():
        if len(node.edges) <= 2 or 'P' in node_id or node_id in ['DEPOT', 'GATE']:
            node.has_light = False; continue
        if 200 < node.x < 1100 and 150 < node.y < 750:
            node.has_light = True
            if enabled: node.light_duration = random.randint(200, 350)
            else: node.light_duration = random.choice([60, 600]) 
            node.light_timer = node.light_duration
            node.light_state = 'H_GREEN'
        else: node.has_light = False
    return True

def emergency_csp(ambulance_path, graph):
    for i in range(len(ambulance_path) - 1):
        curr_id = ambulance_path[i]
        next_id = ambulance_path[i+1]
        node = graph.nodes[next_id]
        if node.has_light:
            dx = node.x - graph.nodes[curr_id].x
            dy = node.y - graph.nodes[curr_id].y
            axis = 'H' if abs(dx) > abs(dy) else 'V'
            node.light_state = 'H_GREEN' if axis == 'H' else 'V_GREEN'
            node.csp_locked = True
    return True

def expectimax_roundabout(state, depth, is_max_turn):
    if depth == 0: return -10 if state == "WAITING" else 10
    if is_max_turn: return max(expectimax_roundabout("PROGRESS", depth - 1, False), expectimax_roundabout("WAITING", depth - 1, False))
    else: return 0.3 * -1000 + 0.7 * 1000 if state == "PROGRESS" else 10
