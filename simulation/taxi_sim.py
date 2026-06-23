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

EDGE_NODES = ['N10', 'N24', 'N31', 'N27', 'N13', 'N20', 'N45', 'N57', 'N82', 'N81', 'N80', 'N79', 'N38', 'N37', 'N35', 'N6', 'N1', 'N17']

def init_custom_map():
    g = Graph()
    for n_id, pos in nodes_data.items():
        label = 'MALL' if n_id in ['N84', 'N91'] else ''
        g.add_node(n_id, pos[0], pos[1], label=label)

    seen_edges = set()
    for u, v in edges_data:
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
        next_choices = [e for e in edges_data if e[0] == current]
        if next_choices:
            next_node = random.choice(next_choices)[1]
            path.append(next_node)
            current = next_node
        else:
            break
            
    if len(path) > 1:
        v.set_path(path, graph)
    else:
        v.x, v.y = nodes_data[start_node]
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
    except Exception:
        bg_image = None

    graph = init_custom_map()
    renderer = Renderer(screen, font, bold_font, title_font)
    dashboard = Dashboard()
    
    vehicles = [create_random_civilian(graph) for _ in range(10)]
    customers = []
    focused_vehicle = None
    is_paused = False

    broken_edges = {} 
    obstacle_mode = False

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_result = dashboard.handle_click(event.pos, graph, vehicles, broken_edges, event.button)
                
                if click_result == "pause":
                    is_paused = not is_paused
                elif click_result == "stop":
                    is_paused = not is_paused
                    if is_paused: dashboard.add_log("HỆ THỐNG: Đã dừng toàn bộ thời gian")
                    else: clock.tick(FPS); dashboard.add_log("HỆ THỐNG: Tiếp tục mô phỏng")
                        
                elif click_result == "reset":
                    vehicles = [create_random_civilian(graph) for _ in range(10)]
                    customers.clear()
                    broken_edges.clear() 
                    focused_vehicle = None
                    is_paused = False
                    obstacle_mode = False
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
                        focused_vehicle = None
                        customers.extend(spawn_scenario_customers(map_id, graph))
                        dashboard.add_log(f"Đã tạo khách cho MAP {map_id}")
                    elif click_result[0] == "SPAWN_TAXI":
                        group_id = click_result[1]
                        algo = click_result[2]
                        spawn_taxi(group_id, algo, graph, vehicles, Vehicle)
                        dashboard.add_log(f"Đã xuất phát xe: {algo}")
                    elif click_result[0] == "FOCUS":
                        focused_vehicle = click_result[1]
                    elif click_result[0] == "NODE":
                        focused_vehicle = None
                    
                    elif click_result[0] == "EDGE" and obstacle_mode:
                        _, u, v_id, proj_pos, edge_dir = click_result
                        edge_key = tuple(sorted((u, v_id)))
                        
                        edge_forward = (u, v_id)
                        edge_backward = (v_id, u)
                        
                        obs_id = f"ROCK_{edge_key[0]}_{edge_key[1]}"
                        
                        if obs_id not in broken_edges:
                            broken_edges[obs_id] = {
                                'pos': proj_pos,
                                'edges': [edge_forward, edge_backward]
                            }
                        
                    elif click_result[0] == "REMOVE_BLOCK":
                        obs_id = click_result[1]
                        if obs_id in broken_edges:
                            del broken_edges[obs_id]

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
                
                # Nếu xe không còn bị hòn đá nào chặn nữa, tự động chuyển về MOVING để di chuyển tiếp
                if not is_stuck and v.state == "STUCK_AT_OBSTACLE":
                    v.state = "MOVING"

                if v.state == "STUCK_AT_OBSTACLE": 
                    continue

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
                if v.state not in ["SAFE_WAIT", "STUCK_AT_OBSTACLE"]:
                    v.state = "MOVING"

                if not v.target_node_id:
                    if v.current_node_id in EDGE_NODES and v.v_id.startswith('CIV_'):
                        vehicles.remove(v)
                        vehicles.append(create_random_civilian(graph))
                        continue
                    else:
                        current = v.current_node_id
                        next_choices = [e for e in edges_data if e[0] == current]
                        
                        valid_choices = []
                        for e in next_choices:
                            in_obstacle = False
                            for obs in broken_edges.values():
                                if (current, e[1]) in obs['edges']: in_obstacle = True; break
                            if not in_obstacle: valid_choices.append(e)

                        if valid_choices:
                            v.set_path([current, random.choice(valid_choices)[1]], graph)
                        elif next_choices: 
                            v.set_path([current, random.choice(next_choices)[1]], graph)

                v.update_position(graph)

        screen.fill(COLOR_BG)
        if bg_image:
            screen.blit(bg_image, (0, 0))

        renderer.draw_graph(graph, broken_edges, customers, set(), False)
        renderer.draw_vehicles(vehicles, graph, focused_vehicle, False, set())
        renderer.draw_dashboard(dashboard.log_messages, dashboard.ui_rects, is_paused, '', False)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_simulation()