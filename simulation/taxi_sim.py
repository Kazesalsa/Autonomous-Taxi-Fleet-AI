import os
import sys
import pygame
import random
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from core.graph import Graph
from core.vehicle import Vehicle
from ai.algorithms import dynamic_routing_a_star, optimize_traffic_lights_sa, emergency_csp, bfs_find_nearest_taxi, get_reachable_network, online_search_replanning, v2v_rescue_bfs
from ui.renderer import Renderer
from ui.dashboard import Dashboard

nodes_data = {
    'N1': (43, 200), 'N2': (111, 200), 'N3': (110, 322), 'N5': (363, 630), 'N6': (3, 630),
    'N7': (391, 313), 'N8': (391, 129), 'N9': (499, 127), 'N10': (499, 0), 'N12': (915, 322),
    'N13': (1122, 322), 'N14': (363, 322), 'N15': (110, 630), 'N16': (915, 630), 'N17': (46, 220),
    'N20': (1124, 299), 'N21': (91, 302), 'N22': (391, 629), 'N23': (392, 368), 'N24': (468, 0),
    'N25': (468, 110), 'N26': (917, 110), 'N27': (917, 2), 'N28': (363, 111), 'N29': (363, 298),
    'N31': (886, 3), 'N32': (888, 630), 'N33': (885, 651), 'N35': (3, 651), 'N36': (90, 651),
    'N37': (90, 777), 'N38': (220, 862), 'N39': (641, 862), 'N41': (1015, 862), 'N42': (1015, 658),
    'N43': (980, 631), 'N44': (884, 847), 'N45': (1247, 631), 'N46': (1140, 631), 'N47': (1109, 663),
    'N48': (1107, 758), 'N49': (1015, 760), 'N50': (1142, 650), 'N51': (1142, 752), 'N54': (1016, 781),
    'N55': (1119, 774), 'N56': (1074, 781), 'N57': (1247, 650), 'N58': (983, 652), 'N59': (983, 848),
    'N60': (641, 651), 'N61': (641, 847), 'N62': (917, 847), 'N63': (917, 651), 'N64': (113, 650),
    'N65': (888, 323), 'N66': (915, 297), 'N67': (915, 128), 'N68': (885, 110), 'N69': (91, 220),
    'N70': (111, 299), 'N71': (884, 299), 'N72': (608, 861), 'N73': (608, 653), 'N74': (640, 630),
    'N75': (113, 770), 'N76': (222, 847), 'N77': (607, 847), 'N78': (608, 740), 'N79': (608, 899),
    'N80': (640, 899), 'N81': (981, 899), 'N82': (1014, 897), 'N83': (228, 299), 'N84': (640, 541),
    'N85': (741, 541), 'N86': (739, 487), 'N87': (916, 487), 'N88': (887, 474), 'N89': (719, 474),
    'N90': (719, 529), 'N91': (607, 530)
}

edges_data = [
    ('N7', 'N8'), ('N8', 'N9'), ('N9', 'N10'), ('N3', 'N14'), ('N15', 'N6'), ('N5', 'N15'), 
    ('N22', 'N23'), ('N23', 'N7'), ('N24', 'N25'), ('N26', 'N27'), ('N14', 'N7'), ('N12', 'N13'), 
    ('N32', 'N33'), ('N35', 'N36'), ('N36', 'N37'), ('N37', 'N38'), ('N38', 'N39'), ('N39', 'N41'), 
    ('N42', 'N43'), ('N33', 'N44'), ('N45', 'N46'), ('N48', 'N49'), ('N49', 'N42'), ('N41', 'N54'), 
    ('N54', 'N49'), ('N54', 'N56'), ('N56', 'N55'), ('N55', 'N51'), ('N51', 'N50'), ('N50', 'N57'), 
    ('N47', 'N48'), ('N46', 'N47'), ('N46', 'N43'), ('N43', 'N16'), ('N58', 'N59'), ('N59', 'N44'), 
    ('N39', 'N61'), ('N44', 'N61'), ('N61', 'N60'), ('N60', 'N33'), ('N33', 'N63'), ('N59', 'N62'), 
    ('N62', 'N63'), ('N63', 'N58'), ('N58', 'N50'), ('N32', 'N63'), ('N16', 'N33'), ('N64', 'N15'), 
    ('N36', 'N64'), ('N66', 'N67'), ('N26', 'N67'), ('N9', 'N67'), ('N67', 'N26'), ('N14', 'N65'), 
    ('N65', 'N13'), ('N31', 'N68'), ('N28', 'N29'), ('N29', 'N14'), ('N15', 'N3'), ('N2', 'N1'), 
    ('N17', 'N69'), ('N69', 'N21'), ('N21', 'N36'), ('N25', 'N28'), ('N3', 'N70'), ('N70', 'N2'), 
    ('N20', 'N66'), ('N66', 'N71'), ('N71', 'N29'), ('N68', 'N71'), ('N68', 'N25'), ('N71', 'N12'), 
    ('N65', 'N12'), ('N64', 'N73'), ('N73', 'N60'), ('N60', 'N74'), ('N32', 'N74'), ('N74', 'N22'), 
    ('N22', 'N5'), ('N75', 'N64'), ('N76', 'N75'), ('N77', 'N72'), ('N61', 'N77'), ('N77', 'N76'), 
    ('N72', 'N79'), ('N80', 'N39'), ('N72', 'N61'), ('N73', 'N78'), ('N78', 'N77'), ('N39', 'N77'), 
    ('N59', 'N81'), ('N41', 'N82'), ('N74', 'N84'), ('N84', 'N85'), ('N85', 'N86'), ('N86', 'N87'), 
    ('N16', 'N87'), ('N87', 'N12'), ('N88', 'N89'), ('N89', 'N90'), ('N90', 'N91'), ('N91', 'N73'), 
    ('N65', 'N88'), ('N88', 'N32'), ('N7', 'N29'), ('N29', 'N83'), ('N83', 'N70')
]

# Cập nhật danh sách điểm rìa bản đồ dựa trên map mới
EDGE_NODES = ['N10', 'N24', 'N31', 'N27', 'N13', 'N20', 'N45', 'N57', 'N82', 'N81', 'N80', 'N79', 'N38', 'N37', 'N35', 'N6', 'N1', 'N17']

def init_custom_map():
    g = Graph()
    
    ORIGINAL_WIDTH = 918
    ORIGINAL_HEIGHT = 865
    scale_x = MAP_WIDTH / ORIGINAL_WIDTH
    scale_y = HEIGHT / ORIGINAL_HEIGHT
    
    # Khởi tạo bãi đỗ xe và gắn cổng ra vào N21 (Một điểm có thật trên bản đồ của bạn)
    g.add_node('DEPOT', 100 * scale_x, 50 * scale_y, label='')
    g.add_node('GATE', 91 * scale_x, 302 * scale_y, label='GATE')
    for i in range(1, 5): g.add_node(f'P{i}', (30 + (i-1)*35) * scale_x, 40 * scale_y, label='')
    for i in range(5, 9): g.add_node(f'P{i}', (30 + (i-5)*35) * scale_x, 80 * scale_y, label='')
    for i in range(1, 9): g.add_bidirectional_edge(f'P{i}', 'GATE')
    
    # Thêm nút vào Graph (Giữ nguyên các thẻ theo yêu cầu)
    for n_id, pos in nodes_data.items():
        if n_id == 'N83':
            g.add_node(n_id, pos[0] * scale_x, pos[1] * scale_y, label='HOSPITAL')
        elif n_id in ['N84', 'N91']:
            g.add_node(n_id, pos[0] * scale_x, pos[1] * scale_y, label='MALL')
        else:
            g.add_node(n_id, pos[0] * scale_x, pos[1] * scale_y, label='')

    # Nối các điểm 1 chiều sử dụng đúng hàm của hệ thống gốc
    seen_edges = set()
    for u, v in edges_data:
        if u in g.nodes and v in g.nodes:
            if (u, v) not in seen_edges:
                g.add_directional_edge(u, v)
                seen_edges.add((u, v))

    # Gắn cổng GATE vào hệ thống giao thông tại N21
    g.add_bidirectional_edge('GATE', 'N21')

    return g

def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Taxi Fleet Management - Advanced Safety Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 15)
    bold_font = pygame.font.SysFont("Arial", 15, bold=True)
    title_font = pygame.font.SysFont("Arial", 22, bold=True)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_image_path = os.path.join(base_dir, "map.png")
    
    try:
        bg_image = pygame.image.load(map_image_path).convert()
        bg_image = pygame.transform.scale(bg_image, (MAP_WIDTH, HEIGHT))
    except Exception as e:
        bg_image = None

    graph = init_custom_map()
    renderer = Renderer(screen, font, bold_font, title_font)
    dashboard = Dashboard()
    
    vehicles = []
    civilian_vehicles = []
    
    # Tạo xe Taxi AI
    for i in range(1, 9):
        v = Vehicle(f"TAXI_{i}", f'P{i}')
        vehicles.append(v)
        
    broken_edges = {}
    customers = []
    
    is_paused = False
    show_fog = False
    select_mode = ''
    select_start_node = None

    optimize_traffic_lights_sa(graph, True)
    dashboard.add_log("HỆ THỐNG: Đã kích hoạt AI. Tối đa 15 xe dân sự.")

    running = True

    while running:
        all_cars = vehicles + civilian_vehicles

        if not is_paused:
            # Điều khiển đèn bằng Simulated Annealing
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
            
            edges_to_remove = []
            for e_id, data in broken_edges.items():
                if data['type'] == 'CROSSWALK':
                    data['timer'] -= 1
                    if data['timer'] <= 0: edges_to_remove.append(e_id)
            
            for e_id in edges_to_remove:
                if e_id in broken_edges:
                    del broken_edges[e_id]
                    e1 = graph.get_edge(e_id[0], e_id[1])
                    e2 = graph.get_edge(e_id[1], e_id[0])
                    if e1: e1.traffic_factor = 0
                    if e2: e2.traffic_factor = 0
                    dashboard.add_log("HỆ THỐNG: Người qua đường xong.")
                    for v in all_cars:
                        if v.state == "WAIT_CROSSWALK":
                            curr_e = tuple(sorted((v.current_edge_start_id, v.target_node_id))) if v.target_node_id else None
                            if curr_e == e_id: v.state = "MOVING"

            # SINH XE DÂN SỰ (Tối đa 15 xe, chỉ đi từ mép này sang mép kia)
            if random.random() < 0.02 and len(civilian_vehicles) < 15:
                start_node = random.choice(EDGE_NODES)
                end_node = random.choice(EDGE_NODES)
                if start_node != end_node:
                    # Dùng thuật toán A* để xe tự tìm đường đến đích
                    path = dynamic_routing_a_star(graph, start_node, end_node, broken_edges_set=broken_edges)
                    if path:
                        civ = Vehicle(f"CIV_{random.randint(100, 999)}", start_node)
                        civ.set_path(path, graph)
                        civ.state = "MOVING"
                        civ.color = random.choice(CIV_COLORS)
                        civilian_vehicles.append(civ)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = dashboard.handle_click(event.pos, graph, vehicles, broken_edges)
                
                if action == "pause": is_paused = not is_paused
                elif action == "fog": show_fog = not show_fog
                elif action == "customer": select_mode = 'CUST_START'
                elif action == "crosswalk": select_mode = 'CROSS'
                elif action == "obstacle": select_mode = 'OBS'
                elif action == "ambulance": select_mode = 'AMB_START'

                elif isinstance(action, tuple):
                    if action[0] == "REMOVE_BLOCK":
                        edge_id = action[1]
                        if edge_id in broken_edges:
                            is_cw = broken_edges[edge_id]['type'] == 'CROSSWALK'
                            del broken_edges[edge_id]
                            e1, e2 = graph.get_edge(edge_id[0], edge_id[1]), graph.get_edge(edge_id[1], edge_id[0])
                            if e1: e1.traffic_factor = 0
                            if e2: e2.traffic_factor = 0
                            dashboard.add_log(f"ĐÃ XÓA: Xóa sự kiện tại {edge_id[0]}-{edge_id[1]}!")
                            for v in all_cars:
                                if not is_cw and v.state in ["STUCK_AT_OBSTACLE", "WAIT_U_TURN"]:
                                    if v.state == "WAIT_U_TURN":
                                        p = online_search_replanning(graph, v.current_node_id, v.target_node_id, v.final_goal_id, broken_edges, is_amb=getattr(v, 'is_ambulance', False))
                                        if p:
                                            v.state = "MOVING"
                                            v.path = p[1:] if len(p) > 1 else []
                                            v.new_path_pending = None
                                    elif v.state == "STUCK_AT_OBSTACLE":
                                        p = online_search_replanning(graph, v.current_node_id, None, v.final_goal_id, broken_edges, is_amb=getattr(v, 'is_ambulance', False))
                                        if p:
                                            v.state = "MOVING"
                                            v.target_node_id = p[1] if len(p) > 1 else None
                                            v.path = p[2:] if len(p) > 2 else []
                                            v.stuck_target = None
                                elif is_cw and v.state == "WAIT_CROSSWALK":
                                    curr_e = tuple(sorted((v.current_edge_start_id, v.target_node_id))) if v.target_node_id else None
                                    if curr_e == edge_id: v.state = "MOVING"

                    elif action[0] == "NODE" and select_mode:
                        if select_mode == 'CUST_START' and 'P' not in action[1] and action[1] != 'GATE':
                            select_start_node = action[1]
                            select_mode = 'CUST_GOAL'
                        elif select_mode == 'CUST_GOAL':
                            if action[1] != select_start_node and 'P' not in action[1]:
                                customers.append({'start': select_start_node, 'goal': action[1], 'status': 'WAITING'})
                                dashboard.add_log(f"KHÁCH HÀNG: Cần xe từ {select_start_node} đến {action[1]}")
                                
                                # Thuật toán BFS Tìm xe gần nhất
                                taxi = bfs_find_nearest_taxi(graph, select_start_node, vehicles)
                                if taxi:
                                    dashboard.add_log(f"BFS: TÌM THẤY {taxi.v_id} rảnh gần nhất.")
                                    start_search = taxi.target_node_id if taxi.target_node_id else taxi.current_node_id
                                    # Thuật toán A* để tính tuyến đường
                                    p_to_cust = dynamic_routing_a_star(graph, start_search, select_start_node, broken_edges_set=broken_edges)
                                    
                                    if p_to_cust:
                                        taxi.status = "TO_CUSTOMER"
                                        taxi.customer_goal = action[1]
                                        if taxi.state == "IDLE_IN_DEPOT":
                                            taxi.state = "MOVING"
                                            taxi.set_path(p_to_cust, graph)
                                        else:
                                            taxi.path = p_to_cust[1:] if taxi.target_node_id else p_to_cust
                                            dashboard.add_log(f"ONLINE SEARCH: {taxi.v_id} bẻ lái đón khách!")
                                else:
                                    dashboard.add_log("CẢNH BÁO: Bãi hết xe rảnh!")
                            select_mode = ''
                        
                        elif select_mode == 'AMB_START':
                            goal_n = 'HOSPITAL'
                            amb = Vehicle(f"AMB_{len(vehicles)}", action[1], is_ambulance=True)
                            amb.state = "MOVING"
                            p = dynamic_routing_a_star(graph, action[1], goal_n, ignore_traffic=True, broken_edges_set=broken_edges)
                            if p: 
                                amb.set_path(p, graph); vehicles.append(amb)
                                # Thuật toán CSP Ưu tiên dọn đường
                                emergency_csp(amb.path, graph)
                                dashboard.add_log(f"CSP: Cứu thương xuất phát hướng BỆNH VIỆN")
                            select_mode = ''

                    elif action[0] == "EDGE" and select_mode in ['CROSS', 'OBS']:
                        _, u_id, v_id, proj, edge_dir = action
                        edge_id = tuple(sorted((u_id, v_id)))
                        if edge_id not in broken_edges:
                            if select_mode == 'CROSS':
                                broken_edges[edge_id] = {'pos': proj, 'type': 'CROSSWALK', 'dir': edge_dir, 'timer': 300, 'discovered': True}
                                e1, e2 = graph.get_edge(u_id, v_id), graph.get_edge(v_id, u_id)
                                if e1: e1.traffic_factor = 0.8
                                if e2: e2.traffic_factor = 0.8
                                dashboard.add_log(f"SỰ KIỆN: Người qua đường")
                            else:
                                obs_type = random.choice(['ROCK', 'LOG'])
                                broken_edges[edge_id] = {'pos': proj, 'type': obs_type, 'discovered': False}
                                dashboard.add_log(f"SỰ CỐ: Rơi {obs_type}. Chờ hệ thống LiDAR phát hiện!")
                            select_mode = ''

        if not is_paused:
            for v in all_cars:
                if v.state not in ["IDLE_IN_DEPOT", "STUCK_AT_OBSTACLE"] and v.target_node_id:
                    curr_edge = tuple(sorted((v.current_edge_start_id, v.target_node_id)))
                    if curr_edge in broken_edges:
                        obs = broken_edges[curr_edge]
                        if obs['type'] in ['ROCK', 'LOG'] and not obs.get('discovered', False):
                            dist_to_obs = math.hypot(v.x - obs['pos'][0], v.y - obs['pos'][1])
                            dx, dy = obs['pos'][0] - v.x, obs['pos'][1] - v.y
                            v_dx, v_dy = graph.nodes[v.target_node_id].x - graph.nodes[v.current_edge_start_id].x, graph.nodes[v.target_node_id].y - graph.nodes[v.current_edge_start_id].y
                            mag = max(0.001, math.hypot(v_dx, v_dy))
                            dot = (dx * (v_dx/mag)) + (dy * (v_dy/mag))
                            
                            if dot > 0 and dist_to_obs < SENSOR_RANGE:
                                obs['discovered'] = True
                                e1, e2 = graph.get_edge(curr_edge[0], curr_edge[1]), graph.get_edge(curr_edge[1], curr_edge[0])
                                if e1: e1.traffic_factor = float('inf')
                                if e2: e2.traffic_factor = float('inf')
                                dashboard.add_log(f"CẢM BIẾN: {getattr(v, 'v_id', 'CIV')} phát hiện vật cản. V2V Broadcast!")
                                
                                for ov in all_cars:
                                    if ov != v and ov.state not in ["IDLE_IN_DEPOT", "STUCK_AT_OBSTACLE"]:
                                        path_edges = [tuple(sorted((ov.path[i], ov.path[i+1]))) for i in range(len(ov.path)-1)] if ov.path else []
                                        ov_curr_e = tuple(sorted((ov.current_edge_start_id, ov.target_node_id))) if ov.target_node_id else None
                                        
                                        if curr_edge in path_edges or (ov_curr_e == curr_edge and ov.state not in ["WAIT_U_TURN", "U_TURNING"]):
                                            np = online_search_replanning(graph, ov.current_node_id, ov.target_node_id, ov.final_goal_id, broken_edges, is_amb=getattr(ov, 'is_ambulance', False))
                                            if np: 
                                                if ov_curr_e == curr_edge:
                                                    ov.state = "WAIT_U_TURN"
                                                    ov.new_path_pending = np
                                                else:
                                                    ov.path = np[1:]
                                            else:
                                                if ov_curr_e == curr_edge:
                                                    ov.state = "STUCK_AT_OBSTACLE"
                                                    ov.stuck_target = obs['pos']
                                                    ov.path = []
                                                    ov.target_node_id = None
                                            
                                if v.state not in ["WAIT_U_TURN", "U_TURNING"]:
                                    p = online_search_replanning(graph, v.current_node_id, v.current_edge_start_id, v.final_goal_id, broken_edges, is_amb=getattr(v, 'is_ambulance', False))
                                    if p:
                                        dashboard.add_log(f"ONLINE SEARCH: {getattr(v, 'v_id', 'CIV')} CHUẨN BỊ QUAY ĐẦU!")
                                        v.state = "WAIT_U_TURN"
                                        v.new_path_pending = p
                                    else:
                                        v.state = "STUCK_AT_OBSTACLE"
                                        v.stuck_target = obs['pos']
                                        v.path = []
                                        v.target_node_id = None
            
            for v in all_cars:
                if v.state == "STUCK_AT_OBSTACLE" and v.stuck_target:
                    dx, dy = v.stuck_target[0] - v.x, v.stuck_target[1] - v.y
                    if math.hypot(dx, dy) < 50: 
                        pass
                    else:
                        v.x += (dx/max(0.001, math.hypot(dx,dy))) * VEHICLE_SPEED_BASE * 0.5
                        v.y += (dy/max(0.001, math.hypot(dx,dy))) * VEHICLE_SPEED_BASE * 0.5

            for v in all_cars:
                if v.state not in ["IDLE_IN_DEPOT", "STUCK_AT_OBSTACLE", "WAIT_U_TURN", "U_TURNING"] and v.target_node_id:
                    curr_e = tuple(sorted((v.current_edge_start_id, v.target_node_id)))
                    if curr_e in broken_edges and broken_edges[curr_e]['type'] == 'CROSSWALK':
                        c_pos = broken_edges[curr_e]['pos']
                        dx, dy = c_pos[0] - v.x, c_pos[1] - v.y
                        v_dx, v_dy = graph.nodes[v.target_node_id].x - graph.nodes[v.current_edge_start_id].x, graph.nodes[v.target_node_id].y - graph.nodes[v.current_edge_start_id].y
                        mag = max(0.001, math.hypot(v_dx, v_dy))
                        dot = (dx * (v_dx/mag)) + (dy * (v_dy/mag))
                        if 0 < dot < 60: v.state = "WAIT_CROSSWALK"

            for v in all_cars:
                if v.state == "WAIT_U_TURN":
                    can_turn = True
                    for v2 in all_cars:
                        if v2 != v and v2.state not in ["WAIT_U_TURN", "U_TURNING", "STUCK_AT_OBSTACLE", "IDLE_IN_DEPOT"]:
                            if v2.target_node_id == v.current_edge_start_id and v2.current_edge_start_id == v.target_node_id:
                                if math.hypot(v.x - v2.x, v.y - v2.y) < 150: can_turn = False; break
                    if can_turn:
                        v.state = "U_TURNING"
                        v.start_uturn_angle = v.angle

            for v in all_cars: 
                if v.state not in ["U_TURNING", "STUCK_AT_OBSTACLE", "WAIT_U_TURN", "WAIT_CROSSWALK", "IDLE_IN_DEPOT", "SAFE_WAIT"]: 
                    v.state = "MOVING"
                v.pull_over_offset = 0.0 # Ép cứng không có độ lệch

            edge_groups = {}
            for v in all_cars:
                if v.target_node_id and v.state not in ["STUCK_AT_OBSTACLE", "U_TURNING", "WAIT_U_TURN", "IDLE_IN_DEPOT"]:
                    edge = (v.current_edge_start_id, v.target_node_id)
                    if edge not in edge_groups: edge_groups[edge] = []
                    edge_groups[edge].append(v)

            # LUẬT GIAO THÔNG: Giữ khoảng cách tối thiểu, không vượt nhau (Tất cả chạy 1 hàng dọc)
            for edge, cars in edge_groups.items():
                tn = graph.nodes[edge[1]]
                cars.sort(key=lambda c: math.hypot(c.x - tn.x, c.y - tn.y))
                
                # Kiểm tra va chạm: Xe sau phải dừng nếu xe trước quá gần
                for i in range(1, len(cars)):
                    d1 = math.hypot(cars[i-1].x - tn.x, cars[i-1].y - tn.y)
                    d2 = math.hypot(cars[i].x - tn.x, cars[i].y - tn.y)
                    if d2 - d1 < 45 and not getattr(cars[i], 'is_ambulance', False): 
                        if cars[i].state != "WAIT_CROSSWALK": cars[i].state = "SAFE_WAIT"
                    elif d2 - d1 < 45 and getattr(cars[i], 'is_ambulance', False) and getattr(cars[i-1], 'is_ambulance', False):
                        cars[i].state = "SAFE_WAIT"

                # Xử lý khi có xe cứu thương phía sau: Các xe dân sự/Taxi đứng im chờ
                ambs = [c for c in cars if getattr(c, 'is_ambulance', False)]
                if ambs:
                    amb_dist = math.hypot(ambs[0].x - tn.x, ambs[0].y - tn.y)
                    for c in cars:
                        if not getattr(c, 'is_ambulance', False):
                            c_dist = math.hypot(c.x - tn.x, c.y - tn.y)
                            # Nếu xe cứu thương ở phía sau và khoảng cách gần, tự động dừng lại (không tấp lề nữa)
                            if c_dist < amb_dist and (amb_dist - c_dist) < 220:
                                c.state = "SAFE_WAIT"
            # Cập nhật TAXI và Cứu thương
            for v in vehicles[:]:
                if v.update_position(graph):
                    if getattr(v, 'is_ambulance', False): 
                        vehicles.remove(v)
                        continue
                    
                    if v.status == "TO_CUSTOMER":
                        for c in customers:
                            if c['start'] == v.current_node_id and c['status'] == 'WAITING':
                                c['status'] = 'PICKED_UP'
                                v.status = "CARRYING"
                                dashboard.add_log(f"HỆ THỐNG: {v.v_id} đã đón khách!")
                                p = dynamic_routing_a_star(graph, v.current_node_id, c['goal'], broken_edges_set=broken_edges)
                                if p: v.set_path(p, graph)
                                break
                    elif v.status == "CARRYING":
                        for c in customers:
                            if c['goal'] == v.current_node_id and c['status'] == 'PICKED_UP':
                                customers.remove(c)
                                v.status = "RETURNING"
                                v.customer_goal = None
                                dashboard.add_log(f"HỆ THỐNG: {v.v_id} trả khách, quay về Bãi.")
                                p = dynamic_routing_a_star(graph, v.current_node_id, 'GATE', broken_edges_set=broken_edges)
                                if p: v.set_path(p, graph)
                                break
                    elif v.status == "RETURNING" and v.current_node_id == 'GATE':
                        occupied_slots = [vx.current_node_id for vx in vehicles if vx.state == "IDLE_IN_DEPOT"]
                        for i in range(1, 9):
                            if f'P{i}' not in occupied_slots:
                                v.status = "IDLE"
                                v.state = "IDLE_IN_DEPOT"
                                v.current_node_id = f'P{i}'
                                v.target_node_id = None
                                break

            # Cập nhật XE DÂN SỰ (Biến mất khi đến điểm mép bản đồ)
            for civ in civilian_vehicles[:]:
                if civ.update_position(graph):
                    civilian_vehicles.remove(civ)

        reachable_nodes, reachable_edges = set(), set()
        if show_fog: reachable_nodes, reachable_edges = get_reachable_network(graph, 'GATE', broken_edges)

        screen.fill(COLOR_BG)
        
        if bg_image:
            screen.blit(bg_image, (0, 0))

        # Khách hàng và Chướng ngại vật
        for c in customers:
            if c['status'] == 'WAITING':
                c_n = graph.nodes[c['start']]
                pygame.draw.circle(screen, COLOR_CUSTOMER, (int(c_n.x), int(c_n.y)), 12)
            if c['status'] in ['WAITING', 'PICKED_UP']:
                g_n = graph.nodes[c['goal']]
                pygame.draw.circle(screen, COLOR_DESTINATION, (int(g_n.x), int(g_n.y)), 12, 3)

        for e_id, obs in broken_edges.items():
            pos = obs['pos']
            color = (255, 100, 100) if obs['type'] == 'CROSSWALK' else (255, 165, 0)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 8)

        # Vẽ xe Taxi, Cứu thương
        renderer.draw_vehicles(vehicles, graph, None, show_fog, set())
        
        # Vẽ xe dân sự (Ngẫu nhiên màu)
        for civ in civilian_vehicles:
            surf = pygame.Surface((18, 9), pygame.SRCALPHA)
            surf.fill(getattr(civ, 'color', (100, 100, 255)))
            pygame.draw.rect(surf, (30, 30, 30), (12, 1, 4, 7))
            rotated_surf = pygame.transform.rotate(surf, -civ.angle)
            rect = rotated_surf.get_rect(center=(int(civ.x), int(civ.y)))
            screen.blit(rotated_surf, rect)

        renderer.draw_dashboard(dashboard.log_messages, dashboard.ui_rects, is_paused, select_mode, show_fog)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_simulation()
