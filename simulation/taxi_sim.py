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
    'N1_GOC': (36, 189), 'N1_PHAI': (36, 203), 'N2_GOC': (65, 188), 'N2_PHAI': (79, 188),
    'N3_GOC': (65, 292), 'N3_PHAI': (79, 292), 'N4_GOC': (105, 292), 'N4_PHAI': (105, 306),
    'N5_GOC': (145, 292), 'N5_PHAI': (145, 306), 'N6_GOC': (198, 292), 'N6_PHAI': (198, 306),
    'N30_GOC': (270, 294), 'N30_PHAI': (284, 294), 'N29_GOC': (358, 287), 'N29_PHAI': (358, 301),
    'N8_GOC': (428, 291), 'N8_PHAI': (428, 305), 'N27_GOC': (523, 290), 'N27_PHAI': (523, 304),
    'N28_GOC': (577, 294), 'N28_PHAI': (577, 308), 'N9_GOC': (664, 295), 'N9_PHAI': (664, 309),
    'N24_GOC': (732, 293), 'N24_PHAI': (732, 307), 'N25_GOC': (770, 294), 'N25_PHAI': (770, 308),
    'N26_GOC': (801, 295), 'N26_PHAI': (801, 309), 'N10_GOC': (270, 226), 'N10_PHAI': (284, 226),
    'N11_GOC': (271, 195), 'N11_PHAI': (285, 195), 'N12_GOC': (272, 165), 'N12_PHAI': (286, 165),
    'N13_GOC': (273, 131), 'N13_PHAI': (287, 131), 'N14_GOC': (274, 106), 'N14_PHAI': (288, 106),
    'N15_GOC': (349, 104), 'N15_PHAI': (349, 118), 'N16_GOC': (346, 6), 'N16_PHAI': (360, 6),
    'N17_GOC': (497, 107), 'N17_PHAI': (497, 121), 'N18_GOC': (595, 107), 'N18_PHAI': (595, 121),
    'N53_GOC': (399, 107), 'N53_PHAI': (399, 121), 'N54_GOC': (444, 110), 'N54_PHAI': (444, 124),
    'N55_GOC': (541, 106), 'N55_PHAI': (541, 120), 'N19_GOC': (658, 105), 'N19_PHAI': (672, 105),
    'N20_GOC': (661, 11), 'N20_PHAI': (675, 11), 'N21_GOC': (661, 49), 'N21_PHAI': (675, 49),
    'N22_GOC': (664, 168), 'N22_PHAI': (678, 168), 'N23_GOC': (662, 209), 'N23_PHAI': (676, 209),
    'N45_GOC': (65, 312), 'N45_PHAI': (79, 312), 'N46_GOC': (65, 336), 'N46_PHAI': (79, 336),
    'N47_GOC': (65, 363), 'N47_PHAI': (79, 363), 'N48_GOC': (65, 400), 'N48_PHAI': (79, 400),
    'N49_GOC': (65, 435), 'N49_PHAI': (79, 435), 'N50_GOC': (64, 464), 'N50_PHAI': (78, 464),
    'N51_GOC': (65, 499), 'N51_PHAI': (79, 499), 'N52_GOC': (65, 527), 'N52_PHAI': (79, 527),
    'N31_GOC': (269, 330), 'N31_PHAI': (283, 330), 'N32_GOC': (270, 367), 'N32_PHAI': (284, 367),
    'N33_GOC': (270, 408), 'N33_PHAI': (284, 408), 'N34_GOC': (268, 447), 'N34_PHAI': (282, 447),
    'N35_GOC': (270, 474), 'N35_PHAI': (284, 474), 'N36_GOC': (267, 510), 'N36_PHAI': (281, 510),
    'N37_GOC': (654, 324), 'N37_PHAI': (678, 324), 'N38_GOC': (653, 357), 'N38_PHAI': (677, 357),
    'N39_GOC': (652, 400), 'N39_PHAI': (676, 400), 'N40_GOC': (651, 437), 'N40_PHAI': (675, 437),
    'N41_GOC': (660, 469), 'N41_PHAI': (674, 469), 'N42_GOC': (653, 496), 'N42_PHAI': (677, 496),
    'N43_GOC': (651, 521), 'N43_PHAI': (675, 521), 'N44_GOC': (661, 543), 'N44_PHAI': (675, 543),
    'N56': (72, 600), 'N57': (278, 600), 'N58': (459, 602), 'N62': (912, 605), 'N63': (1, 603), 
    'N64': (9, 627), 'N69': (279, 626), 'N70': (667, 626), 'N71': (912, 627), 'N73': (112, 728), 
    'N74': (156, 771), 'N76': (112, 631), 'N77': (197, 807), 'N78': (265, 813), 'N79': (329, 814), 
    'N80': (402, 813), 'N81': (439, 814), 'N82': (447, 666), 'N83': (448, 739), 'N84': (446, 768), 
    'N85': (449, 792), 'N86': (448, 843), 'N88': (651, 771), 'N89': (653, 809), 'N90': (470, 809), 
    'N91': (469, 854), 'N92': (467, 648), 'N93': (469, 627), 'N94': (437, 606), 'N96': (649, 668), 
    'N98': (676, 810), 'N99': (670, 650), 'N101': (649, 603), 'N102': (679, 601), 'N103': (746, 812), 
    'N104': (747, 674), 'N105': (741, 619), 'N106': (721, 654), 'N107': (722, 701), 'N108': (721, 728), 
    'N109': (722, 763), 'N110': (726, 830), 'N111': (530, 828), 'N112': (485, 825), 'N113': (213, 828), 
    'N114': (156, 815), 'N115': (78, 747), 'N116': (75, 674), 'N117': (72, 636), 'N118': (840, 642), 
    'N122': (838, 725), 'N123': (840, 681), 'N124': (815, 746), 'N125': (774, 751), 'N126': (755, 752), 
    'N127': (771, 726), 'N128': (800, 726), 'N130': (819, 668), 'N131': (818, 648), 'N132': (817, 705), 
    'N133': (72, 562),
    'N134': (164, 266), 'N135': (573, 793), 'N136': (459, 522), 'N137': (743, 288), 'N138': (856, 606)
}

edges_data = [
    ('N1_GOC', 'N2_GOC'), ('N2_GOC', 'N3_GOC'), ('N3_PHAI', 'N2_PHAI'), ('N2_PHAI', 'N1_PHAI'),
    ('N26_GOC', 'N25_GOC'), ('N25_GOC', 'N24_GOC'), ('N24_GOC', 'N9_GOC'), ('N9_GOC', 'N28_GOC'),
    ('N28_GOC', 'N27_GOC'), ('N27_GOC', 'N8_GOC'), ('N8_GOC', 'N29_GOC'), ('N29_GOC', 'N30_GOC'),
    ('N30_GOC', 'N6_GOC'), ('N6_GOC', 'N5_GOC'), ('N5_GOC', 'N4_GOC'), ('N4_GOC', 'N3_GOC'),
    ('N3_PHAI', 'N4_PHAI'), ('N4_PHAI', 'N5_PHAI'), ('N5_PHAI', 'N6_PHAI'), ('N6_PHAI', 'N30_PHAI'),
    ('N30_PHAI', 'N29_PHAI'), ('N29_PHAI', 'N8_PHAI'), ('N8_PHAI', 'N27_PHAI'), ('N27_PHAI', 'N28_PHAI'),
    ('N28_PHAI', 'N9_PHAI'), ('N9_PHAI', 'N24_PHAI'), ('N24_PHAI', 'N25_PHAI'), ('N25_PHAI', 'N26_PHAI'),
    ('N3_GOC', 'N45_GOC'), ('N45_GOC', 'N46_GOC'), ('N46_GOC', 'N47_GOC'), ('N47_GOC', 'N48_GOC'),
    ('N48_GOC', 'N49_GOC'), ('N49_GOC', 'N50_GOC'), ('N50_GOC', 'N51_GOC'), ('N51_GOC', 'N52_GOC'),
    ('N52_PHAI', 'N51_PHAI'), ('N51_PHAI', 'N50_PHAI'), ('N50_PHAI', 'N49_PHAI'), ('N49_PHAI', 'N48_PHAI'),
    ('N48_PHAI', 'N47_PHAI'), ('N47_PHAI', 'N46_PHAI'), ('N46_PHAI', 'N45_PHAI'), ('N45_PHAI', 'N3_PHAI'),
    ('N14_GOC', 'N13_GOC'), ('N13_GOC', 'N12_GOC'), ('N12_GOC', 'N11_GOC'), ('N11_GOC', 'N10_GOC'),
    ('N10_GOC', 'N30_GOC'), ('N30_PHAI', 'N10_PHAI'), ('N10_PHAI', 'N11_PHAI'), ('N11_PHAI', 'N12_PHAI'),
    ('N12_PHAI', 'N13_PHAI'), ('N13_PHAI', 'N14_PHAI'), ('N16_GOC', 'N15_GOC'), ('N15_PHAI', 'N16_PHAI'),
    ('N19_GOC', 'N18_GOC'), ('N18_GOC', 'N55_GOC'), ('N55_GOC', 'N17_GOC'), ('N17_GOC', 'N54_GOC'),
    ('N54_GOC', 'N53_GOC'), ('N53_GOC', 'N15_GOC'), ('N15_GOC', 'N14_GOC'), ('N14_PHAI', 'N15_PHAI'),
    ('N15_PHAI', 'N53_PHAI'), ('N53_PHAI', 'N54_PHAI'), ('N54_PHAI', 'N17_PHAI'), ('N17_PHAI', 'N55_PHAI'),
    ('N55_PHAI', 'N18_PHAI'), ('N18_PHAI', 'N19_PHAI'), ('N19_GOC', 'N21_GOC'), ('N21_GOC', 'N20_GOC'),
    ('N20_PHAI', 'N21_PHAI'), ('N21_PHAI', 'N19_PHAI'), ('N19_GOC', 'N22_GOC'), ('N22_GOC', 'N23_GOC'),
    ('N23_GOC', 'N9_GOC'), ('N9_PHAI', 'N23_PHAI'), ('N23_PHAI', 'N22_PHAI'), ('N22_PHAI', 'N19_PHAI'),
    ('N30_GOC', 'N31_GOC'), ('N31_GOC', 'N32_GOC'), ('N32_GOC', 'N33_GOC'), ('N33_GOC', 'N34_GOC'),
    ('N34_GOC', 'N35_GOC'), ('N35_GOC', 'N36_GOC'), ('N36_PHAI', 'N35_PHAI'), ('N35_PHAI', 'N34_PHAI'),
    ('N34_PHAI', 'N33_PHAI'), ('N33_UP', 'N32_PHAI'), ('N32_PHAI', 'N31_PHAI'), ('N31_PHAI', 'N30_PHAI'),
    ('N9_GOC', 'N37_GOC'), ('N37_GOC', 'N38_GOC'), ('N38_GOC', 'N39_GOC'), ('N39_GOC', 'N40_GOC'),
    ('N40_GOC', 'N41_GOC'), ('N41_GOC', 'N42_GOC'), ('N42_GOC', 'N43_GOC'), ('N43_GOC', 'N44_GOC'),
    ('N44_PHAI', 'N43_PHAI'), ('N43_PHAI', 'N42_PHAI'), ('N42_PHAI', 'N41_PHAI'), ('N41_PHAI', 'N40_PHAI'),
    ('N40_PHAI', 'N39_PHAI'), ('N39_PHAI', 'N38_PHAI'), ('N38_PHAI', 'N37_PHAI'), ('N37_PHAI', 'N9_PHAI'),
    ('N56', 'N57'), ('N57', 'N56'), ('N63', 'N56'), ('N56', 'N63'), ('N63', 'N64'), ('N64', 'N63'),
    ('N57', 'N69'), ('N69', 'N57'), ('N70', 'N71'), ('N71', 'N70'), ('N73', 'N74'), ('N74', 'N73'),
    ('N76', 'N69'), ('N69', 'N76'), ('N76', 'N64'), ('N64', 'N76'), ('N76', 'N73'), ('N73', 'N76'),
    ('N74', 'N77'), ('N77', 'N74'), ('N77', 'N78'), ('N78', 'N77'), ('N78', 'N79'), ('N79', 'N78'),
    ('N79', 'N80'), ('N80', 'N79'), ('N80', 'N81'), ('N81', 'N80'), ('N82', 'N83'), ('N83', 'N82'),
    ('N83', 'N84'), ('N84', 'N83'), ('N84', 'N85'), ('N85', 'N84'), ('N85', 'N81'), ('N81', 'N85'),
    ('N81', 'N86'), ('N86', 'N81'), ('N85', 'N86'), ('N86', 'N85'), ('N88', 'N89'), ('N89', 'N88'),
    ('N89', 'N90'), ('N90', 'N89'), ('N91', 'N92'), ('N92', 'N91'), ('N92', 'N93'), ('N93', 'N92'),
    ('N93', 'N70'), ('N70', 'N93'), ('N94', 'N82'), ('N82', 'N94'), ('N57', 'N94'), ('N94', 'N57'),
    ('N69', 'N93'), ('N93', 'N69'), ('N96', 'N88'), ('N88', 'N96'), ('N98', 'N89'), ('N89', 'N98'),
    ('N98', 'N99'), ('N99', 'N98'), ('N94', 'N101'), ('N101', 'N94'), ('N101', 'N102'), ('N102', 'N101'),
    ('N102', 'N62'), ('N62', 'N102'), ('N101', 'N96'), ('N96', 'N101'), ('N102', 'N99'), ('N99', 'N102'),
    ('N98', 'N103'), ('N103', 'N98'), ('N103', 'N104'), ('N104', 'N103'), ('N104', 'N105'), ('N105', 'N104'),
    ('N105', 'N102'), ('N102', 'N105'), ('N106', 'N107'), ('N107', 'N106'), ('N107', 'N108'), ('N108', 'N107'),
    ('N108', 'N109'), ('N109', 'N108'), ('N109', 'N110'), ('N110', 'N109'), ('N110', 'N111'), ('N111', 'N110'),
    ('N90', 'N91'), ('N91', 'N90'), ('N111', 'N112'), ('N112', 'N111'), ('N112', 'N90'), ('N90', 'N112'),
    ('N112', 'N113'), ('N113', 'N112'), ('N113', 'N114'), ('N114', 'N113'), ('N114', 'N115'), ('N115', 'N114'),
    ('N115', 'N116'), ('N116', 'N115'), ('N116', 'N117'), ('N117', 'N116'), ('N64', 'N117'), ('N117', 'N64'),
    ('N122', 'N123'), ('N123', 'N122'), ('N118', 'N123'), ('N123', 'N118'), ('N122', 'N124'), ('N124', 'N122'),
    ('N124', 'N125'), ('N125', 'N124'), ('N125', 'N126'), ('N126', 'N125'), ('N126', 'N103'), ('N103', 'N126'),
    ('N127', 'N128'), ('N128', 'N127'), ('N130', 'N131'), ('N131', 'N130'), ('N131', 'N132'), ('N132', 'N131'),
    ('N132', 'N128'), ('N128', 'N132'), ('N127', 'N108'), ('N108', 'N127'), ('N133', 'N56'), ('N56', 'N133'),
    ('N52_GOC', 'N56'), ('N56', 'N52_PHAI'), ('N52_GOC', 'N117'), ('N117', 'N52_PHAI'),
    ('N117', 'N76'), ('N76', 'N117'), ('N36_GOC', 'N57'), ('N57', 'N36_PHAI'),
    ('N36_GOC', 'N69'), ('N69', 'N36_PHAI'), ('N44_GOC', 'N101'), ('N101', 'N44_PHAI'),
    ('N44_GOC', 'N102'), ('N102', 'N44_PHAI'), ('N44_GOC', 'N70'), ('N70', 'N44_PHAI')
]

# Các mép bản đồ dùng để xe dân sự Sinh ra / Đi ra ngoài
EDGE_NODES = ['N16_GOC', 'N20_GOC', 'N1_GOC', 'N26_GOC', 'N63', 'N62', 'N91', 'N86', 'N110', 'N133']
CIV_COLORS = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50), (50, 200, 200), (200, 50, 200), (255, 128, 0)]

def init_custom_map():
    g = Graph()
    
    # 1. Kích thước cửa sổ gốc lúc bạn lấy tọa độ
    ORIGINAL_WIDTH = 918
    ORIGINAL_HEIGHT = 865
    
    # 2. Kích thước bản đồ được hiển thị thực tế trên hệ thống (Lấy từ config.py)
    # WIDTH = 1600, MAP_WIDTH = 1250, HEIGHT = 900
    scale_x = MAP_WIDTH / ORIGINAL_WIDTH
    scale_y = HEIGHT / ORIGINAL_HEIGHT
    
    g.add_node('DEPOT', 100 * scale_x, 50 * scale_y, label='')
    g.add_node('GATE', 250 * scale_x, 100 * scale_y, label='GATE')
    for i in range(1, 5): g.add_node(f'P{i}', (30 + (i-1)*35) * scale_x, 40 * scale_y, label='')
    for i in range(5, 9): g.add_node(f'P{i}', (30 + (i-5)*35) * scale_x, 80 * scale_y, label='')
    for i in range(1, 9): g.add_bidirectional_edge(f'P{i}', 'GATE')
    
    g.add_node('HOSPITAL', 1150 * scale_x, 100 * scale_y, label='HOSPITAL')

    # Chuyển đổi toàn bộ node sang tọa độ của hệ thống
    for n_id, pos in nodes_data.items():
        g.add_node(n_id, pos[0] * scale_x, pos[1] * scale_y, label='')

    seen_edges = set()
    for u, v in edges_data:
        if u == 'N33_UP': u = 'N33_GOC' 
        if v == 'N33_UP': v = 'N33_GOC'
        if u in g.nodes and v in g.nodes:
            if (u, v) not in seen_edges and (v, u) not in seen_edges:
                g.add_bidirectional_edge(u, v)
                seen_edges.add((u, v))

    g.add_bidirectional_edge('GATE', 'N10_GOC')
    g.add_bidirectional_edge('GATE', 'N14_GOC')
    g.add_bidirectional_edge('HOSPITAL', 'N26_GOC')
    g.add_bidirectional_edge('HOSPITAL', 'N23_GOC')

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
