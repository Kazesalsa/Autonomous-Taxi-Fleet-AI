import os
import sys
import pygame
import random
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from simulation.spawners import spawn_scenario_customers, spawn_taxi
from core.graph import Graph
from core.vehicle import Vehicle
from ui.renderer import Renderer
from ui.dashboard import Dashboard
from algorithms.registry import ALGORITHM_REGISTRY

# Import dữ liệu bản đồ sạch từ module core
from core.map_data import NODES_DATA, EDGES_DATA

EDGE_NODES = ['N1', 'N17', 'N6', 'N35', 'N79', 'N80', 'N82', 'N81', 'N45', 'N57', 'N20', 'N13', 'N27', 'N31', 'N10', 'N24']

def init_custom_map():
    g = Graph()
    for n_id, pos in NODES_DATA.items():
        label = 'MALL' if n_id in ['N84', 'N91'] else ''
        g.add_node(n_id, pos[0], pos[1], label=label)
    seen_edges = set()
    for u, v in EDGES_DATA:
        if u in g.nodes and v in g.nodes and (u, v) not in seen_edges:
            g.add_directional_edge(u, v)
            seen_edges.add((u, v))
    return g

def create_random_civilian(graph):
    start_node = random.choice(EDGE_NODES)
    v = Vehicle(f"CIV_{random.randint(1000, 9999)}", start_node)
    v.color = (random.randint(40, 255), random.randint(40, 255), random.randint(40, 255))
    current = start_node
    path = [current]
    for _ in range(8):
        next_choices = [e for e in EDGES_DATA if e[0] == current]
        if next_choices:
            next_node = random.choice(next_choices)[1]
            path.append(next_node)
            current = next_node
        else: break
    if len(path) > 1: v.set_path(path, graph)
    else: v.x, v.y = NODES_DATA[start_node]
    v.state = "MOVING"
    return v

def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Taxi Fleet Management")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 15)
    bold_font = pygame.font.SysFont("Arial", 15, bold=True)
    title_font = pygame.font.SysFont("Arial", 22, bold=True)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        bg_image = pygame.image.load(os.path.join(base_dir, "map.png")).convert()
        bg_image = pygame.transform.scale(bg_image, (MAP_WIDTH, HEIGHT))
    except Exception: bg_image = None

    graph = init_custom_map()
    renderer = Renderer(screen, font, bold_font, title_font)
    dashboard = Dashboard()
    
    vehicles = [create_random_civilian(graph) for _ in range(10)]
    customers = []
    is_paused = False
    broken_edges = {} 
    obstacle_mode = False

    is_scenario_3_active = False
    last_spawn_time = 0

    running = True
    while running:
        clock.tick(FPS)

        if is_scenario_3_active:
            current_time = pygame.time.get_ticks()
            if current_time - last_spawn_time >= 15000:
                all_nodes = list(graph.nodes.keys())
                new_batch = []
                for i in range(4):
                    st, gl = random.choice(all_nodes), random.choice(all_nodes)
                    while gl == st: gl = random.choice(all_nodes)
                    new_batch.append({'id': f"CUST_M3_ADD_{pygame.time.get_ticks()}_{i+1}", 'start': st, 'goal': gl})
                customers.extend(new_batch)
                last_spawn_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_result = dashboard.handle_click(event.pos, graph, vehicles, broken_edges, event.button)
                
                if click_result == "pause": is_paused = not is_paused
                elif click_result == "stop":
                    is_paused = not is_paused
                    if is_paused: dashboard.add_log("HỆ THỐNG: Đã dừng toàn bộ thời gian")
                    else: clock.tick(FPS); dashboard.add_log("HỆ THỐNG: Tiếp tục mô phỏng")
                elif click_result == "reset":
                    vehicles = [create_random_civilian(graph) for _ in range(10)]
                    customers.clear()
                    broken_edges.clear() 
                    is_paused, obstacle_mode, is_scenario_3_active = False, False, False
                    dashboard.ui_rects['_state_sync']['obstacle_mode'] = False
                    dashboard.add_log("HỆ THỐNG: Đã reset toàn bộ bản đồ")
                elif click_result == "obstacle":
                    obstacle_mode = not obstacle_mode
                    dashboard.ui_rects['_state_sync']['obstacle_mode'] = obstacle_mode
                elif isinstance(click_result, tuple):
                    if click_result[0] == "START_SCENARIO":
                        map_id = click_result[1]
                        vehicles = [v for v in vehicles if v.v_id.startswith('CIV_')]
                        customers.clear()
                        broken_edges.clear()
                        is_scenario_3_active = (map_id == 3)
                        if is_scenario_3_active: last_spawn_time = pygame.time.get_ticks()
                        
                        customers.extend(spawn_scenario_customers(map_id, graph))
                        dashboard.add_log(f"Đã tạo khách cho MAP {map_id}")

                    elif click_result[0] == "SPAWN_TAXI":
                        group_id = click_result[1]
                        algo = click_result[2]
                        
                        v = spawn_taxi(group_id, algo, graph, vehicles, Vehicle)
                        
                        unassigned_customer = None
                        for cust in customers:
                            is_assigned = any(getattr(x, 'customer_goal', None) == cust['goal'] for x in vehicles if x.v_id.startswith('TX_'))
                            if not is_assigned:
                                unassigned_customer = cust
                                break
                        
                        if unassigned_customer:
                            cust_start, cust_goal = unassigned_customer['start'], unassigned_customer['goal']
                            v.customer_goal = cust_goal
                            
                            if v.current_node_id == cust_start:
                                safe_nodes = [n for n in graph.nodes.keys() if n != cust_start]
                                if safe_nodes:
                                    v.current_node_id = random.choice(safe_nodes)
                                    v.current_edge_start_id = v.current_node_id
                                    v.x = graph.nodes[v.current_node_id].x
                                    v.y = graph.nodes[v.current_node_id].y

                            if algo in ALGORITHM_REGISTRY:
                                to_pickup_path = ALGORITHM_REGISTRY[algo](graph, v.current_node_id, cust_start)
                                to_goal_path = ALGORITHM_REGISTRY[algo](graph, cust_start, cust_goal)
                                
                                if to_pickup_path and to_goal_path:
                                    full_path = to_pickup_path + to_goal_path[1:]
                                    v.set_path(full_path, graph)
                                    dashboard.add_log(f"ĐÓN KHÁCH: Xe {algo} xuất phát từ {v.current_node_id} đi đón khách tại {cust_start}")
                                else:
                                    dashboard.add_log(f"CẢNH BÁO: Thuật toán {algo} không tìm đủ đường đi đón/trả!")
                            else: dashboard.add_log(f"LỖI: Thuật toán {algo} chưa đăng ký!")
                        else: dashboard.add_log(f"Đã xuất phát xe tuần tra từ Depot: {algo} (Không có khách)")
                    
                    elif click_result[0] == "EDGE" and obstacle_mode:
                        _, u, v_id, proj_pos, edge_dir = click_result
                        edge_key = tuple(sorted((u, v_id)))
                        obs_id = f"ROCK_{edge_key[0]}_{edge_key[1]}"
                        if obs_id not in broken_edges:
                            broken_edges[obs_id] = {'pos': proj_pos, 'edges': [(edge_key[0], edge_key[1]), (edge_key[1], edge_key[0])]}
                    elif click_result[0] == "REMOVE_BLOCK":
                        obs_id = click_result[1]
                        if obs_id in broken_edges: del broken_edges[obs_id]

        if not is_paused:
            edge_groups = {}
            for v in vehicles:
                is_stuck = False
                if v.target_node_id:
                    current_edge = (v.current_edge_start_id, v.target_node_id)
                    for obs in broken_edges.values():
                        if current_edge in obs['edges']:
                            if math.hypot(v.x - obs['pos'][0], v.y - obs['pos'][1]) < 35:
                                v.state = "STUCK_AT_OBSTACLE"
                                is_stuck = True
                                break
                if not is_stuck and v.state == "STUCK_AT_OBSTACLE": v.state = "MOVING"
                if v.state == "STUCK_AT_OBSTACLE": continue

                if v.target_node_id and v.state != "STUCK_AT_OBSTACLE":
                    edge = (v.current_edge_start_id, v.target_node_id)
                    if edge not in edge_groups: edge_groups[edge] = []
                    edge_groups[edge].append(v)

            for edge, cars in edge_groups.items():
                tn = graph.nodes[edge[1]]
                cars.sort(key=lambda c: math.hypot(c.x - tn.x, c.y - tn.y))
                if cars: cars[0].state = "MOVING"
                for i in range(1, len(cars)):
                    d1 = math.hypot(cars[i-1].x - tn.x, cars[i-1].y - tn.y)
                    d2 = math.hypot(cars[i].x - tn.x, cars[i].y - tn.y)
                    cars[i].state = "SAFE_WAIT" if (d2 - d1 < 45) else "MOVING"

            for v in vehicles:
                if v.state not in ["SAFE_WAIT", "STUCK_AT_OBSTACLE"]: v.state = "MOVING"
                if not v.target_node_id:
                    if v.current_node_id in EDGE_NODES and v.v_id.startswith('CIV_'):
                        vehicles.remove(v)
                        vehicles.append(create_random_civilian(graph))
                        continue
                    else:
                        current = v.current_node_id
                        next_choices = [e for e in EDGES_DATA if e[0] == current]
                        valid_choices = []
                        for e in next_choices:
                            in_obstacle = False
                            for obs in broken_edges.values():
                                if (current, e[1]) in obs['edges']: in_obstacle = True; break
                            if not in_obstacle: valid_choices.append(e)
                        if valid_choices: v.set_path([current, random.choice(valid_choices)[1]], graph)
                        elif next_choices: v.set_path([current, random.choice(next_choices)[1]], graph)

                v.update_position(graph)

                if v.v_id.startswith('TX_') and getattr(v, 'customer_goal', None):
                    if not getattr(v, 'has_picked_up', False) and v.current_node_id:
                        for cust in list(customers):
                            if cust['goal'] == v.customer_goal and cust['start'] == v.current_node_id:
                                v.has_picked_up = True
                                customers.remove(cust)
                                dashboard.add_log(f"HỆ THỐNG: Xe {v.v_id.split('_')[2]} đã đón khách thành công.")
                                break
                    if getattr(v, 'has_picked_up', False) and v.current_node_id == v.customer_goal:
                        dashboard.add_log(f"HỆ THỐNG: Xe {v.v_id.split('_')[2]} đã hoàn thành trả khách.")
                        v.customer_goal = None
                        v.has_picked_up = False

        taxi_leaderboard = {}
        for v in vehicles:
            if v.v_id.startswith('TX_'):
                parts = v.v_id.split("_")
                display_name = f"{parts[2]}_{parts[1]}" if len(parts) >= 3 else v.v_id
                dist = int(getattr(v, 'distance_traveled', 0))
                rev = int(getattr(v, 'revenue_earned', 0))
                taxi_leaderboard[display_name] = {'distance': dist, 'revenue': rev, 'state': v.state}
        dashboard.metrics['taxi_leaderboard'] = taxi_leaderboard
        dashboard._sync_state()

        screen.fill(COLOR_BG)
        if bg_image: screen.blit(bg_image, (0, 0))
        renderer.draw_graph(graph, broken_edges, customers, set(), False)
        renderer.draw_vehicles(vehicles, graph, None, False, set())
        renderer.draw_dashboard(dashboard.log_messages, dashboard.ui_rects, is_paused, '', False)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__": run_simulation()