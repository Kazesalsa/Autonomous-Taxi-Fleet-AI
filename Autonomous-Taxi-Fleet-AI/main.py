import os
import sys
import pygame
import random
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from core.graph import Graph
from core.vehicle import Vehicle
from ai.algorithms import dynamic_routing_a_star, optimize_traffic_lights_sa, emergency_csp, bfs_find_nearest_taxi, expectimax_roundabout, online_search_replanning
from ui.renderer import Renderer
from ui.dashboard import Dashboard

def init_maze_city_graph():
    g = Graph()
    # Depot Area
    g.add_node('DEPOT', 150, 100, label='')
    g.add_node('GATE', 250, 150, label='GATE')
    for i in range(1, 9):
        px = 80 + (i-1)*25 if i <= 4 else 80 + (i-5)*25
        py = 70 if i <= 4 else 120
        g.add_node(f'P{i}', px, py, label='')
        g.add_bidirectional_edge(f'P{i}', 'GATE')
    
    # 6x5 Maze Grid
    cols, rows = 7, 5
    spacing_x, spacing_y = 160, 150
    offset_x, offset_y = 250, 150
    
    for r in range(rows):
        for c in range(cols):
            n_id = f'N_{r}_{c}'
            g.add_node(n_id, offset_x + c * spacing_x, offset_y + r * spacing_y, label=f'{r},{c}')

    # Create Maze connections (removing some to make it maze-like)
    for r in range(rows):
        for c in range(cols):
            curr = f'N_{r}_{c}'
            if c < cols - 1 and not (r == 1 and c == 2) and not (r == 3 and c == 4): 
                g.add_bidirectional_edge(curr, f'N_{r}_{c+1}')
            if r < rows - 1 and not (r == 2 and c == 1) and not (r == 1 and c == 5):
                g.add_bidirectional_edge(curr, f'N_{r+1}_{c}')
                
    g.add_bidirectional_edge('GATE', 'N_0_0')
    g.add_bidirectional_edge('GATE', 'N_1_0')
    return g

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Taxi Fleet Management - Maze Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 15)
    bold_font = pygame.font.SysFont("Arial", 15, bold=True)
    title_font = pygame.font.SysFont("Arial", 22, bold=True)

    graph = init_maze_city_graph()
    renderer = Renderer(screen, font, bold_font, title_font)
    dashboard = Dashboard()
    
    vehicles = []
    # Spawn 8 Taxis in Depot
    for i in range(1, 9):
        v = Vehicle(f"TAXI_{i}", f'P{i}')
        vehicles.append(v)
        
    broken_edges = {}
    customers = []
    
    is_paused = False
    select_mode = ''
    select_start_node = None

    optimize_traffic_lights_sa(graph, True)
    dashboard.add_log("HỆ THỐNG: Khởi tạo bãi đỗ 8 Taxi thành công.")

    running = True

    while running:
        if not is_paused:
            for node_id, node in graph.nodes.items():
                if not node.csp_locked and node.has_light:
                    node.light_timer -= 1
                    if node.light_timer <= 0:
                        if node.light_state == 'H_GREEN':
                            node.light_state = 'H_YELLOW'
                            node.light_timer = node.yellow_duration
                        elif node.light_state == 'H_YELLOW':
                            node.light_state = 'V_GREEN'
                            node.light_timer = node.light_duration
                        elif node.light_state == 'V_GREEN':
                            node.light_state = 'V_YELLOW'
                            node.light_timer = node.yellow_duration
                        elif node.light_state == 'V_YELLOW':
                            node.light_state = 'H_GREEN'
                            node.light_timer = node.light_duration
            
            # Quản lý sự kiện đường phố
            edges_to_remove = []
            for e_id, data in broken_edges.items():
                if data['type'] == 'CROSSWALK':
                    data['timer'] -= 1
                    if data['timer'] <= 0: edges_to_remove.append(e_id)
            
            for e_id in edges_to_remove:
                del broken_edges[e_id]
                graph.get_edge(e_id[0], e_id[1]).traffic_factor = 0
                graph.get_edge(e_id[1], e_id[0]).traffic_factor = 0
                dashboard.add_log("HỆ THỐNG: Người đã qua đường xong.")
                # Đánh thức xe
                for v in vehicles:
                    if v.state == "WAIT_CROSSWALK": v.state = "MOVING"

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = dashboard.handle_click(event.pos, graph, vehicles)
                
                if action == "pause":
                    is_paused = not is_paused
                elif action == "customer": select_mode = 'CUST_START'
                elif action == "crosswalk": select_mode = 'CROSS'
                elif action == "obstacle": select_mode = 'OBS'
                elif action == "ambulance": select_mode = 'AMB_START'

                elif isinstance(action, tuple):
                    if action[0] == "NODE" and select_mode:
                        if select_mode == 'CUST_START' and 'P' not in action[1] and action[1] != 'GATE':
                            select_start_node = action[1]
                            select_mode = 'CUST_GOAL'
                        elif select_mode == 'CUST_GOAL':
                            if action[1] != select_start_node and 'P' not in action[1]:
                                customers.append({'start': select_start_node, 'goal': action[1], 'status': 'WAITING'})
                                dashboard.add_log(f"KHÁCH HÀNG: Cần xe từ {select_start_node} đến {action[1]}")
                                
                                # BFS TÌM XE
                                taxi = bfs_find_nearest_taxi(graph, select_start_node, vehicles)
                                if taxi:
                                    dashboard.add_log(f"BFS: TÌM THẤY {taxi.v_id} gần nhất, đang điều phối.")
                                    # Nếu xe đang ngoài đường (RETURNING), online replan
                                    start_search = taxi.target_node_id if taxi.target_node_id else taxi.current_node_id
                                    p_to_cust = dynamic_routing_a_star(graph, start_search, select_start_node, broken_edges_set=broken_edges)
                                    
                                    if p_to_cust:
                                        taxi.status = "TO_CUSTOMER"
                                        taxi.customer_goal = action[1]
                                        if taxi.state == "IDLE_IN_DEPOT":
                                            taxi.state = "MOVING"
                                            taxi.set_path(p_to_cust, graph)
                                        else:
                                            # Đang đi đường, bẻ lái
                                            taxi.path = p_to_cust[1:] if taxi.target_node_id else p_to_cust
                                            dashboard.add_log(f"ONLINE SEARCH: {taxi.v_id} bẻ lái đón khách mới!")
                                else:
                                    dashboard.add_log("CẢNH BÁO: Bãi hết xe rảnh!")
                                select_mode = ''
                        
                        elif select_mode == 'AMB_START':
                            goal_n = random.choice([n for n in graph.nodes.keys() if 'P' not in n and n != action[1]])
                            amb = Vehicle(f"AMB_{len(vehicles)}", action[1], is_ambulance=True)
                            amb.state = "MOVING"
                            p = dynamic_routing_a_star(graph, action[1], goal_n, ignore_traffic=True)
                            if p: 
                                amb.set_path(p, graph); vehicles.append(amb)
                                emergency_csp(amb.path, graph)
                                dashboard.add_log(f"CSP: Dẹp đường cho cứu thương {action[1]}->{goal_n}")
                            select_mode = ''

                    elif action[0] == "EDGE" and select_mode in ['CROSS', 'OBS']:
                        _, u_id, v_id, proj, edge_dir = action
                        edge_id = tuple(sorted((u_id, v_id)))
                        if edge_id not in broken_edges:
                            if select_mode == 'CROSS':
                                broken_edges[edge_id] = {'pos': proj, 'type': 'CROSSWALK', 'dir': edge_dir, 'timer': 300}
                                graph.get_edge(u_id, v_id).traffic_factor = 0.8
                                graph.get_edge(v_id, u_id).traffic_factor = 0.8
                                dashboard.add_log(f"SỰ KIỆN: Người qua đường tại {u_id}-{v_id}")
                            else:
                                obs_type = random.choice(['ROCK', 'LOG'])
                                broken_edges[edge_id] = {'pos': proj, 'type': obs_type}
                                graph.get_edge(u_id, v_id).traffic_factor = float('inf')
                                graph.get_edge(v_id, u_id).traffic_factor = float('inf')
                                dashboard.add_log(f"SỰ CỐ TAI NẠN: Chặn tại {u_id}-{v_id}")
                                
                                # Online Replanning for blocked cars
                                for v in vehicles:
                                    if v.state != "IDLE_IN_DEPOT" and not v.is_ambulance:
                                        curr_e = tuple(sorted((v.current_edge_start_id, v.target_node_id))) if v.target_node_id else None
                                        if curr_e == edge_id:
                                            p = online_search_replanning(graph, v.current_node_id, v.current_edge_start_id, v.final_goal_id, broken_edges)
                                            if p:
                                                dashboard.add_log(f"ONLINE SEARCH: {v.v_id} QUAY ĐẦU NÉ TAI NẠN!")
                                                v.state = "WAIT_U_TURN"
                                                v.new_path_pending = p
                                            else:
                                                v.state = "STUCK_AT_OBSTACLE"
                                                v.stuck_target = proj
                                                v.path = []
                                                v.target_node_id = None
                                        else:
                                            path_nodes = [v.current_edge_start_id, v.target_node_id] + v.path if v.target_node_id else [v.current_node_id] + v.path
                                            path_edges = [tuple(sorted((path_nodes[i], path_nodes[i+1]))) for i in range(len(path_nodes)-1)]
                                            if edge_id in path_edges:
                                                p = online_search_replanning(graph, v.current_node_id, v.target_node_id, v.final_goal_id, broken_edges)
                                                if p: v.path = p[1:]
                                                else:
                                                    v.state = "STUCK_AT_OBSTACLE"
                                                    v.stuck_target = proj
                                                    v.path = []
                                                    v.target_node_id = None
                            select_mode = ''

        if not is_paused:
            # Check Obstacle distances (Stop 40px BEFORE obstacle)
            for v in vehicles:
                if v.state == "STUCK_AT_OBSTACLE" and v.stuck_target:
                    dx, dy = v.stuck_target[0] - v.x, v.stuck_target[1] - v.y
                    if math.hypot(dx, dy) < 40: # Phanh khoảng cách an toàn
                        pass # Đứng im
                    else:
                        v.x += (dx/math.hypot(dx,dy)) * VEHICLE_SPEED_BASE * 0.5
                        v.y += (dy/math.hypot(dx,dy)) * VEHICLE_SPEED_BASE * 0.5

            # Check Crosswalk distances
            for v in vehicles:
                if v.state not in ["IDLE_IN_DEPOT", "STUCK_AT_OBSTACLE", "WAIT_U_TURN", "U_TURNING"] and v.target_node_id:
                    curr_e = tuple(sorted((v.current_edge_start_id, v.target_node_id)))
                    if curr_e in broken_edges and broken_edges[curr_e]['type'] == 'CROSSWALK':
                        c_pos = broken_edges[curr_e]['pos']
                        
                        # Tính khoảng cách từ xe đến đường cắt ngang của vạch kẻ đường
                        dx, dy = c_pos[0] - v.x, c_pos[1] - v.y
                        v_dx, v_dy = graph.nodes[v.target_node_id].x - graph.nodes[v.current_edge_start_id].x, graph.nodes[v.target_node_id].y - graph.nodes[v.current_edge_start_id].y
                        mag = math.hypot(v_dx, v_dy)
                        if mag > 0:
                            # Tích vô hướng để biết vạch kẻ ở phía trước hay sau xe
                            dot = (dx * (v_dx/mag)) + (dy * (v_dy/mag))
                            if 0 < dot < 50: # Nếu vạch kẻ ở ngay phía trước < 50px
                                v.state = "WAIT_CROSSWALK"

            for v in vehicles:
                if v.state == "WAIT_U_TURN":
                    can_turn = True
                    for v2 in vehicles:
                        if v2 != v and v2.state not in ["WAIT_U_TURN", "U_TURNING", "STUCK_AT_OBSTACLE", "IDLE_IN_DEPOT"]:
                            if v2.target_node_id == v.current_edge_start_id and v2.current_edge_start_id == v.target_node_id:
                                if math.hypot(v.x - v2.x, v.y - v2.y) < 150: can_turn = False; break
                    if can_turn:
                        v.state = "U_TURNING"
                        v.start_uturn_angle = v.angle

            for v in vehicles: 
                if v.state not in ["U_TURNING", "STUCK_AT_OBSTACLE", "WAIT_U_TURN", "WAIT_CROSSWALK", "IDLE_IN_DEPOT"]: v.state = "MOVING"
                
                target_offset = 0.0
                if v.state == "YIELD_INNER" and not v.is_ambulance: target_offset = 4
                elif v.state == "YIELD_OUTER" and not v.is_ambulance: target_offset = 12
                
                if v.pull_over_offset < target_offset: v.pull_over_offset += 1.5
                elif v.pull_over_offset > target_offset: v.pull_over_offset -= 1.5

            edge_groups = {}
            for v in vehicles:
                if v.target_node_id and v.state not in ["STUCK_AT_OBSTACLE", "U_TURNING", "WAIT_U_TURN", "IDLE_IN_DEPOT"]:
                    edge = (v.current_edge_start_id, v.target_node_id)
                    if edge not in edge_groups: edge_groups[edge] = []
                    edge_groups[edge].append(v)

            for edge, cars in edge_groups.items():
                tn = graph.nodes[edge[1]]
                cars.sort(key=lambda c: math.hypot(c.x - tn.x, c.y - tn.y))
                
                for l in [0, 1]:
                    lane_cars = [c for c in cars if c.lane == l]
                    for i in range(1, len(lane_cars)):
                        d1 = math.hypot(lane_cars[i-1].x - tn.x, lane_cars[i-1].y - tn.y)
                        d2 = math.hypot(lane_cars[i].x - tn.x, lane_cars[i].y - tn.y)
                        if d2 - d1 < 40 and not lane_cars[i].is_ambulance: 
                            if lane_cars[i].state != "WAIT_CROSSWALK": lane_cars[i].state = "SAFE_WAIT"
                        elif d2 - d1 < 40 and lane_cars[i].is_ambulance and lane_cars[i-1].is_ambulance:
                            lane_cars[i].state = "SAFE_WAIT"

                ambs = [c for c in cars if c.is_ambulance]
                if ambs:
                    amb_dist = math.hypot(ambs[0].x - tn.x, ambs[0].y - tn.y)
                    for c in cars:
                        if not c.is_ambulance:
                            c_dist = math.hypot(c.x - tn.x, c.y - tn.y)
                            if c_dist < amb_dist and (amb_dist - c_dist) < 220:
                                if c.lane == 0: c.state = "YIELD_INNER"
                                else: c.state = "YIELD_OUTER"

            # Vehicle Logic update
            for v in vehicles[:]:
                if v.update_position(graph):
                    if v.is_ambulance: vehicles.remove(v); continue
                    
                    if v.status == "TO_CUSTOMER":
                        for c in customers:
                            if c['start'] == v.current_node_id and c['status'] == 'WAITING':
                                c['status'] = 'PICKED_UP'
                                v.status = "CARRYING"
                                dashboard.add_log(f"HỆ THỐNG: {v.v_id} đã đón khách, A* tiến về đích.")
                                p = dynamic_routing_a_star(graph, v.current_node_id, c['goal'], broken_edges_set=broken_edges)
                                if p: v.set_path(p, graph)
                                break
                    elif v.status == "CARRYING":
                        for c in customers:
                            if c['goal'] == v.current_node_id and c['status'] == 'PICKED_UP':
                                customers.remove(c)
                                v.status = "RETURNING"
                                v.customer_goal = None
                                dashboard.add_log(f"HỆ THỐNG: {v.v_id} trả khách thành công. Quay về Depot.")
                                # Find path back to depot gate
                                p = dynamic_routing_a_star(graph, v.current_node_id, 'GATE', broken_edges_set=broken_edges)
                                if p: v.set_path(p, graph)
                                break
                    elif v.status == "RETURNING" and v.current_node_id == 'GATE':
                        # Tìm slot trống trong bãi
                        occupied_slots = [vx.current_node_id for vx in vehicles if vx.state == "IDLE_IN_DEPOT"]
                        for i in range(1, 9):
                            if f'P{i}' not in occupied_slots:
                                v.status = "IDLE"
                                v.state = "IDLE_IN_DEPOT"
                                v.current_node_id = f'P{i}'
                                v.target_node_id = None
                                dashboard.add_log(f"HỆ THỐNG: {v.v_id} đã nhập bãi đỗ.")
                                break

        screen.fill(COLOR_BG)
        renderer.draw_graph(graph, broken_edges, customers)
        renderer.draw_vehicles(vehicles, graph, None)
        renderer.draw_dashboard(dashboard.log_messages, dashboard.ui_rects, is_paused, select_mode)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
