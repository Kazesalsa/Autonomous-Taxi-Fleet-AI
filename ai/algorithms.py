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
            if edge_id not in broken_edges_set or (broken_edges_set[edge_id].get('discovered', True) == False):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append(edge.target_id)
                    network.append(edge.target_id)
    return network

def get_reachable_network(graph, start_id, broken_edges):
    visited_nodes = {start_id}
    visited_edges = set()
    queue = deque([start_id])
    while queue:
        curr = queue.popleft()
        for edge in graph.nodes[curr].edges:
            edge_id = tuple(sorted((curr, edge.target_id)))
            is_blocked = False
            if edge_id in broken_edges:
                if broken_edges[edge_id]['type'] != 'CROSSWALK' and broken_edges[edge_id].get('discovered', False):
                    is_blocked = True
            
            if not is_blocked:
                visited_edges.add(edge_id)
                if edge.target_id not in visited_nodes:
                    visited_nodes.add(edge.target_id)
                    queue.append(edge.target_id)
    return visited_nodes, visited_edges

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
            
            if broken_edges_set and edge_id in broken_edges_set:
                if broken_edges_set[edge_id].get('discovered', False) and broken_edges_set[edge_id]['type'] != 'CROSSWALK':
                    continue 
                    
            weight = edge.distance if ignore_traffic else edge.get_weight()
            if weight == float('inf') and not ignore_traffic: continue
                
            tentative_g = g_score[curr_id] + weight
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = curr_id
                g_score[neighbor_id] = tentative_g
                f_score[neighbor_id] = tentative_g + heuristic(graph.nodes[neighbor_id], goal)
                heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
    return []

def online_search_replanning(graph, current_node, target_node, final_goal, broken_edges_set, is_amb=False):
    start_re = target_node if target_node else current_node
    return dynamic_routing_a_star(graph, start_re, final_goal, ignore_traffic=is_amb, broken_edges_set=broken_edges_set)

def optimize_traffic_lights_sa(graph, enabled=True):
    for node_id, node in graph.nodes.items():
        if len(node.edges) <= 2 or 'P' in node_id or node_id in ['DEPOT', 'GATE', 'HOSPITAL']:
            node.has_light = False; continue
        if 200 < node.x < 1100 and 200 < node.y < 800:
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
