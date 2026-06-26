import os
import sys
import pygame
import random
import math



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *

from simulation.spawners import spawn_taxi
from simulation.traffic_light import TrafficLightManager
from simulation.traffic_flow import TrafficFlowManager
from core.graph import Graph
from core.vehicle import Vehicle, Ambulance, ManualTaxi
from ui.renderer import Renderer
from ui.dashboard import Dashboard
from algorithms.registry import ALGORITHM_REGISTRY
from core.map_data import NODES_DATA, EDGES_DATA

EDGE_NODES = ['N1', 'N17', 'N6', 'N35', 'N79', 'N80', 'N82', 'N81', 'N45', 'N57', 'N20', 'N13', 'N27', 'N31', 'N10', 'N24']

RESTRICTED_NODES = ['N83', 'N105']
RESTRICTED_EDGES_DATA = [e for e in EDGES_DATA if e[0] not in RESTRICTED_NODES and e[1] not in RESTRICTED_NODES]

def init_hospital_ambulances(vehicles_list):
    hospital_nodes = ['N106', 'N103', 'N108', 'N107']
    ambs = []
    for i, node in enumerate(hospital_nodes):
        v = Ambulance(f"AMB_HOSP_{i}", node)
        v.x, v.y = NODES_DATA[node]
        if node in ['N103', 'N108']: v.x += 15
        elif node in ['N106', 'N107']: v.x -= 12
        vehicles_list.append(v)
        ambs.append(v)
    return ambs

def init_custom_map():
    g = Graph()
    g_restricted = Graph()
    for n_id, pos in NODES_DATA.items():
        label = 'MALL' if n_id in ['N84', 'N91'] else ''
        g.add_node(n_id, pos[0], pos[1], label=label)
        g_restricted.add_node(n_id, pos[0], pos[1], label=label)
    
    seen_edges = set()
    for u, v in EDGES_DATA:
        if u in g.nodes and v in g.nodes and (u, v) not in seen_edges:
            g.add_directional_edge(u, v)
            if u not in RESTRICTED_NODES and v not in RESTRICTED_NODES:
                g_restricted.add_directional_edge(u, v)
            seen_edges.add((u, v))
    return g, g_restricted

def create_random_civilian(graph):
    start_node = random.choice(EDGE_NODES)
    v = Vehicle(f"CIV_{random.randint(1000, 9999)}", start_node)
    v.color = (random.randint(40, 255), random.randint(40, 255), random.randint(40, 255))
    current = start_node
    path = [current]
    TAXI_PARKING_NODES = ['N111', 'N112', 'N114', 'N115', 'N116', 'N117']
    for _ in range(8):
        next_choices = [e for e in RESTRICTED_EDGES_DATA if e[0] == current and e[1] not in TAXI_PARKING_NODES]
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

    def get_alpha_label(idx):
        res = ""
        while idx >= 0:
            res = chr(65 + (idx % 26)) + res
            idx = idx // 26 - 1
        return res

    def update_customer_labels_and_fares(customers_list):
        from collections import defaultdict
        groups = defaultdict(list)
        for c in customers_list:
            if not c.get('picked_up') and not c.get('delivered'):
                groups[c['start']].append(c)
        
        for start_node, group in groups.items():
            if len(group) >= 2:
                base_label = str(group[0].get('label', 'A')).split('_')[0]
                for idx, c in enumerate(group):
                    c['label'] = f"{base_label}_{idx+1}"
                    c['fare'] = 15000

    customer_spawn_count = 0
    patient_spawn_count = 1
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Taxi Fleet Management - CSP Active")
    clock = pygame.time.Clock()
    
    pygame.font.init()
    # Try Segoe UI first (sharpest on Windows), fall back to Arial
    _font_candidates = ["Segoe UI", "Calibri", "Arial"]
    _chosen_font = None
    for _f in _font_candidates:
        try:
            _test = pygame.font.SysFont(_f, 19)
            if _test:
                _chosen_font = _f
                break
        except Exception:
            pass
    if not _chosen_font:
        _chosen_font = None  # will use pygame default

    font = pygame.font.SysFont(_chosen_font, 19)
    bold_font = pygame.font.SysFont(_chosen_font, 19, bold=True)
    title_font = pygame.font.SysFont(_chosen_font, 28, bold=True)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        bg_image = pygame.image.load(os.path.join(base_dir, "map.png")).convert()
        bg_image = pygame.transform.smoothscale(bg_image, (MAP_WIDTH, HEIGHT))
    except Exception: bg_image = None

    graph, restricted_graph = init_custom_map()
    renderer = Renderer(screen, font, bold_font, title_font)
    dashboard = Dashboard()
    
    vehicles = [create_random_civilian(graph) for _ in range(40)]
    hospital_ambs = init_hospital_ambulances(vehicles)
    
    customers = []; broken_edges = {} 
    is_paused = False; obstacle_mode = False
    pending_spawn_group = None; pending_spawn_algo = None; focused_vehicle = None; pending_customer_start = None

    traffic_manager = TrafficLightManager()
    traffic_flow = TrafficFlowManager()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_result = dashboard.handle_click(event.pos, graph, vehicles, broken_edges, event.button)
                
                if click_result == "CANCEL_SPAWN":
                    pending_spawn_algo = None
                    pending_spawn_group = None
                    dashboard.active_group = None
                    dashboard._sync_state()
                    dashboard.add_log("Đã huỷ chọn thuật toán spawn xe")
                    continue

                if click_result == "UI_UPDATED":
                    if dashboard.create_mode != "Khách":
                        pending_customer_start = None
                    continue

                if isinstance(click_result, tuple) and click_result[0] == "NODE" and pending_spawn_algo:
                    n_id = click_result[1]
                    if n_id in EDGE_NODES:
                        algo = pending_spawn_algo
                        grp_id = pending_spawn_group
                        v_cls = Vehicle if grp_id == 5 else ManualTaxi
                        v = spawn_taxi(grp_id, algo, n_id, graph, vehicles, v_cls)
                        dashboard.add_log(f"Đã tạo {v.v_id} ({algo}) tại {n_id}")
                    else:
                        dashboard.add_log(f"{n_id} không hợp lệ! Chọn node nằm ở viền bản đồ (A, B, C...)")
                    pending_spawn_algo = None
                    pending_spawn_group = None
                    dashboard.active_group = None
                    dashboard._sync_state()
                    continue

                if isinstance(click_result, tuple) and click_result[0] == "NODE" and not pending_spawn_algo:
                    n_id = click_result[1]
                    create_mode = dashboard.create_mode
                    if create_mode == "Bệnh nhân":
                        cust = {'start': n_id, 'goal': n_id, 'picked_up': False, 'label': f"BN_{len(customers)}", 'is_patient': True}
                        customers.append(cust)
                        idle_ambs = [a for a in hospital_ambs if a.state == "IDLE_AT_HOSPITAL"]
                        if idle_ambs:
                            amb = idle_ambs[0]
                            path_to_patient = ALGORITHM_REGISTRY["A*"](graph, amb.current_node_id, n_id)
                            if path_to_patient:
                                amb.dispatch(n_id, graph, path_to_patient, customer_dict=cust)
                    elif create_mode == "Khách":
                        if not pending_customer_start:
                            pending_customer_start = n_id
                            dashboard.add_log(f"Chọn đích đến cho khách tại {n_id}")
                        else:
                            start_n = pending_customer_start
                            goal_n = n_id
                            if start_n != goal_n:
                                customers.append({'start': start_n, 'goal': goal_n, 'picked_up': False, 'label': get_alpha_label(customer_spawn_count), 'is_manual': True, 'fare': 5000})
                                customer_spawn_count += 1
                                update_customer_labels_and_fares(customers)
                                dashboard.add_log(f"Đã tạo khách ({start_n} -> {goal_n})")
                            pending_customer_start = None

                if isinstance(click_result, tuple) and click_result[0] == "FOCUS":
                    focused_vehicle = click_result[1] if focused_vehicle != click_result[1] else None
                    continue

                if click_result == "pause": is_paused = not is_paused

                elif click_result == "obstacle":
                    obstacle_mode = not obstacle_mode
                    dashboard.add_log(f"Chế độ vật cản: {'Bật - click vào đường để đặt đá' if obstacle_mode else 'Tắt'}")

                elif click_result == "create":
                    modes = ["Khách", "Bệnh nhân"]
                    idx = modes.index(dashboard.create_mode) if dashboard.create_mode in modes else 0
                    dashboard.create_mode = modes[(idx + 1) % len(modes)]
                    dashboard._sync_state(obstacle_mode=obstacle_mode)

                elif isinstance(click_result, tuple) and click_result[0] == "REMOVE_BLOCK":
                    edge_id = click_result[1]
                    if edge_id in broken_edges:
                        del broken_edges[edge_id]
                        dashboard.add_log(f"Đã xóa vật cản")

                elif isinstance(click_result, tuple) and click_result[0] == "EDGE" and obstacle_mode:
                    u_id, v_id, proj, edge_dir = click_result[1], click_result[2], click_result[3], click_result[4]
                    edge_key = f"{u_id}_{v_id}"
                    if edge_key not in broken_edges:
                        broken_edges[edge_key] = {
                            'u': u_id, 'v': v_id,
                            'pos': proj,
                            'dir': edge_dir,
                            'edges': {(u_id, v_id), (v_id, u_id)}
                        }
                        dashboard.add_log(f"Đã đặt vật cản tại {u_id}→{v_id}")
                    else:
                        del broken_edges[edge_key]
                        dashboard.add_log(f"Đã xóa vật cản {u_id}→{v_id}")

                elif isinstance(click_result, tuple) and click_result[0] == "START_SCENARIO":
                    scenario_id = click_result[1]
                    if scenario_id == 2:
                        is_endless_mode = False
                        vehicles = [v for v in vehicles if not v.v_id.startswith('TX_')] # Xoá các taxi hiện có
                        customers.clear()

                        spawn_taxi(5, "Minimax", 'N96', graph, vehicles, Vehicle)
                        spawn_taxi(5, "Alpha-Beta", 'N96', graph, vehicles, Vehicle)
                        spawn_taxi(5, "Expect", 'N96', graph, vehicles, Vehicle)
                        
                        valid_nodes = [n for n in graph.nodes.keys() if n not in RESTRICTED_NODES]
                        scen2_start = random.choice(valid_nodes)
                        scen2_goal = random.choice(valid_nodes)
                        while scen2_goal == scen2_start: scen2_goal = random.choice(valid_nodes)
                        
                        traffic_manager.scen2_start = scen2_start
                        traffic_manager.scen2_goal = scen2_goal

                        for i in range(3):
                            cust = {'start': scen2_start, 'goal': scen2_goal, 'picked_up': False, 'delivered': False, 'label': get_alpha_label(customer_spawn_count), 'fare': 5000, 'is_scenario_2': True}
                            customers.append(cust)
                            customer_spawn_count += 1
                        
                        update_customer_labels_and_fares(customers)
                        dashboard.add_log("Kịch bản 2: Bắt đầu đua!")
                    elif scenario_id == 1:
                        is_endless_mode = False
                        customers.clear()
                        valid_nodes = [n for n in graph.nodes.keys() if n not in RESTRICTED_NODES]
                        for i in range(10):
                            start_node = random.choice(valid_nodes)
                            goal_node = random.choice(valid_nodes)
                            while goal_node == start_node: goal_node = random.choice(valid_nodes)
                            customers.append({'start': start_node, 'goal': goal_node, 'picked_up': False, 'label': get_alpha_label(customer_spawn_count), 'is_manual': False, 'fare': 5000})
                            customer_spawn_count += 1
                        update_customer_labels_and_fares(customers)
                        dashboard.add_log("Đã tự động tạo 10 khách hàng (Kịch bản 1).")

                elif click_result == "reset":
                    vehicles = [create_random_civilian(graph) for _ in range(20)]
                    hospital_ambs = init_hospital_ambulances(vehicles)
                    customers.clear(); broken_edges.clear()
                    obstacle_mode = False
                    traffic_manager.csp_overrides = {}
                    is_paused = False
                elif isinstance(click_result, tuple) and click_result[0] == "SPAWN_TAXI":
                    pending_spawn_group = click_result[1]
                    pending_spawn_algo = click_result[2]
                    dashboard.add_log(f"Chọn node ngoài viền (A,B,C..) để đặt xe {pending_spawn_algo}")

        if not is_paused:

            is_endless = getattr(sys.modules[__name__], 'is_endless_mode', False)
            if is_endless:
                if not hasattr(traffic_manager, 'customer_blueprints'):

                    valid = [n for n in graph.nodes.keys() if n not in RESTRICTED_NODES]
                    traffic_manager.customer_blueprints = valid
                    traffic_manager.active_customers = customers

                while len(traffic_manager.active_customers) < 10:
                    start_node = random.choice(traffic_manager.customer_blueprints)
                    goal_node = random.choice(traffic_manager.customer_blueprints)
                    while goal_node == start_node: goal_node = random.choice(traffic_manager.customer_blueprints)
                    cust = {'start': start_node, 'goal': goal_node, 'picked_up': False, 'delivered': False, 'label': get_alpha_label(customer_spawn_count), 'fare': 5000}
                    customers.append(cust)
                    customer_spawn_count += 1
                
            for v in vehicles:
                if v.v_id.startswith('TX_') and not isinstance(v, ManualTaxi):
                    if not v.target_node_id: 
                        if getattr(v, 'assigned_customers', []):
                            assigned = v.assigned_customers[0]
                            if v.current_node_id == assigned['start'] and not assigned.get('picked_up'):
                                assigned['picked_up'] = True
                                v.has_picked_up = True
                                try:
                                    p = ALGORITHM_REGISTRY[getattr(v, 'algo', 'A*')](restricted_graph, v.current_node_id, assigned['goal'])
                                    if p and len(p) > 1: v.set_path(p, restricted_graph)
                                    else: v.set_path([v.current_node_id, assigned['goal']], restricted_graph)
                                except Exception: pass
                            elif v.current_node_id == assigned['goal'] and assigned.get('picked_up'):
                                assigned['delivered'] = True
                                v.revenue_earned += assigned.get('fare', 10000)
                                v.assigned_customers.clear()
                                v.has_picked_up = False
                                v.completed_trips = getattr(v, 'completed_trips', 0) + 1
                                
                                if assigned.get('is_scenario_2') and hasattr(traffic_manager, 'scen2_start'):
                                    new_cust = {'start': traffic_manager.scen2_start, 'goal': traffic_manager.scen2_goal, 'picked_up': False, 'delivered': False, 'label': get_alpha_label(customer_spawn_count), 'fare': 5000, 'is_scenario_2': True}
                                    customers.append(new_cust)
                                    customer_spawn_count += 1
                                    update_customer_labels_and_fares(customers)
                            elif not v.target_node_id:
                                # Nếu xe bị mất đường (đã đi hết path ngắn hoặc lỗi path) nhưng chưa tới đích, tính lại đường!
                                tgt = assigned['goal'] if assigned.get('picked_up') else assigned['start']
                                try:
                                    p = ALGORITHM_REGISTRY[getattr(v, 'algo', 'A*')](restricted_graph, v.current_node_id, tgt)
                                    if p and len(p) > 1: v.set_path(p, restricted_graph)
                                    else: v.set_path([v.current_node_id, tgt], restricted_graph)
                                except Exception: pass

                        
                        if not getattr(v, 'assigned_customers', []):
                            unassigned = [c for c in customers if not c.get('delivered', False) and not any(c in getattr(x, 'assigned_customers', []) or c is getattr(x, 'customer_dict', None) for x in vehicles if x.v_id.startswith('TX_'))]
                            if unassigned:

                                best_c = min(unassigned, key=lambda c: math.hypot(graph.nodes[c['start']].x - graph.nodes[v.current_node_id].x, graph.nodes[c['start']].y - graph.nodes[v.current_node_id].y))
                                v.assigned_customers.append(best_c)
                                try:
                                    p = ALGORITHM_REGISTRY[getattr(v, 'algo', 'A*')](restricted_graph, v.current_node_id, best_c['start'])
                                    if p and len(p) > 1: v.set_path(p, restricted_graph)
                                    else: v.set_path([v.current_node_id, best_c['start']], restricted_graph)
                                except Exception: pass

            traffic_manager.update(graph, vehicles)
            traffic_flow.check_static_obstacles(vehicles, broken_edges)
            traffic_flow.manage_distances(vehicles, graph, broken_edges)

            for v in vehicles:
                if v.state not in ["SAFE_WAIT", "STUCK_AT_OBSTACLE", "IDLE_AT_HOSPITAL", "MOVING_TO_PATIENT", "RETURNING_TO_HOSPITAL", "IDLE_AT_PARKING", "MOVING_TO_CUSTOMER", "MOVING_TO_GOAL", "RETURNING_TO_PARKING"]:
                    v.state = "MOVING"

                if v.v_id.startswith('TX_'):
                    if getattr(v, 'state', '') not in ["MOVING_TO_CUSTOMER", "MOVING_TO_GOAL"]:
                        TAXI_PARKING_NODES = ['N111', 'N112', 'N114', 'N115', 'N116', 'N117']
                        if v.current_node_id in TAXI_PARKING_NODES:
                            other = [x for x in vehicles if x != v and x.current_node_id == v.current_node_id and getattr(x, 'state', '') == "IDLE_AT_PARKING"]
                            if not other:
                                v.state = "IDLE_AT_PARKING"
                                v.target_node_id = None
                                v.path = []

                if isinstance(v, ManualTaxi):
                    if v.state in ["IDLE_AT_PARKING", "IDLE"]:
                        unassigned = [c for c in customers if not c.get('delivered')]
                        unassigned = [c for c in unassigned if not any(c in getattr(x, 'assigned_customers', []) or c is getattr(x, 'customer_dict', None) for x in vehicles if x.v_id.startswith('TX_'))]
                        if unassigned:

                            best_c = min(unassigned, key=lambda c: math.hypot(graph.nodes[c['start']].x - graph.nodes[v.current_node_id].x, graph.nodes[c['start']].y - graph.nodes[v.current_node_id].y) if c['start'] in graph.nodes and v.current_node_id in graph.nodes else float('inf'))
                            v.dispatch(best_c, graph)

                if not v.target_node_id:
                    if v.current_node_id in EDGE_NODES and v.v_id.startswith('CIV_'):
                        vehicles.remove(v)
                        vehicles.append(create_random_civilian(graph))
                        continue
                    else:
                        current = v.current_node_id
                        if not getattr(v, 'is_ambulance', False) and getattr(v, 'state', '') != "IDLE_AT_PARKING":
                            next_choices = [e for e in RESTRICTED_EDGES_DATA if e[0] == current]
                            if not str(getattr(v, 'v_id', '')).startswith('TX_'):
                                TAXI_PARKING_NODES = ['N111', 'N112', 'N114', 'N115', 'N116', 'N117']
                                next_choices = [e for e in next_choices if e[1] not in TAXI_PARKING_NODES]
                            if next_choices: v.set_path([current, random.choice(next_choices)[1]], graph)

                v.update_position(graph)


            taxi_leaderboard = {}
            for v in vehicles:
                if v.v_id.startswith('TX_'):
                    parts = v.v_id.split("_")
                    display_name = f"{parts[2]}_{parts[1]}" if len(parts) >= 3 else v.v_id
                    cst = int(getattr(v, 'cost', getattr(v, 'distance_traveled', 0) * 10))
                    rev = int(getattr(v, 'revenue', getattr(v, 'revenue_earned', 0)))
                    
                    if hasattr(v, 'assigned_customers') and getattr(v, 'assigned_customers', []):
                        lbls = ",".join([c.get('label', '') for c in v.assigned_customers])
                    elif hasattr(v, 'customer_dict') and getattr(v, 'customer_dict', None):
                        lbls = getattr(v, 'customer_dict').get('label', 'KH')
                    else:
                        lbls = "-"
                        
                    taxi_leaderboard[display_name] = {'cost': cst, 'revenue': rev, 'state': getattr(v, 'state', 'UNK'), 'customers': lbls}
            dashboard.metrics['taxi_leaderboard'] = taxi_leaderboard
        dashboard._sync_state(obstacle_mode=obstacle_mode)
        screen.fill(COLOR_BG)
        if bg_image: screen.blit(bg_image, (0, 0))
        
        spawn_nodes = EDGE_NODES if pending_spawn_algo else None
        traffic_colors = traffic_manager.get_render_data()
        renderer.draw_graph(graph, broken_edges, customers, set(), False, pending_spawn_nodes=spawn_nodes, focused_vehicle=focused_vehicle, traffic_light_colors=traffic_colors)
        renderer.draw_vehicles(vehicles, graph, None, False, set())
        renderer.draw_dashboard(dashboard.log_messages, dashboard.ui_rects, is_paused, '', False)
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__": run_simulation()