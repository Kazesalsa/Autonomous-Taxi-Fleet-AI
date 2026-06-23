import pygame
import sys
import os
import math

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    from config import WIDTH, HEIGHT, MAP_WIDTH
except ImportError:
    WIDTH, HEIGHT, MAP_WIDTH = 918, 865, 918 

NODE_RADIUS = 4
CLICK_RADIUS = 8
ARROW_COLOR = (0, 191, 255) 

def get_distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def get_dist_to_segment(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    
    abs_ab = get_distance(a, b)
    if abs_ab == 0:
        return get_distance(p, a)
        
    t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / (abs_ab ** 2)
    t = max(0, min(1, t))
    
    proj_x = ax + t * (bx - ax)
    proj_y = ay + t * (by - ay)
    
    return get_distance(p, (proj_x, proj_y))

def draw_arrow(screen, color, start, end, arrow_size=8):
    pygame.draw.line(screen, color, start, end, 2)
    
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    end_adj = (end[0] - NODE_RADIUS * math.cos(angle), end[1] - NODE_RADIUS * math.sin(angle))
    
    angle_left = angle - math.pi / 6  
    angle_right = angle + math.pi / 6 
    
    p1 = (end_adj[0] - arrow_size * math.cos(angle_left), end_adj[1] - arrow_size * math.sin(angle_left))
    p2 = (end_adj[0] - arrow_size * math.cos(angle_right), end_adj[1] - arrow_size * math.sin(angle_right))
    
    pygame.draw.polygon(screen, color, [end_adj, p1, p2])

def print_output(clicked_nodes, custom_edges):
    print("\n" + "#"*30 + " DỮ LIỆU ĐỒ THỊ 1 CHIỀU " + "#"*30)
    print("nodes_data = {")
    nodes_str = ",\n    ".join([f"'N{n['id']}': {n['pos']}" for n in sorted(clicked_nodes, key=lambda k: k['id'])])
    print(f"    {nodes_str}")
    print("}\n")
    
    print("edges_data = [")
    formatted_edges = [f"('N{e[0]}', 'N{e[1]}')" for e in custom_edges]
    if formatted_edges:
        print("    " + ", ".join(formatted_edges))
    print("]")
    print("#"*80)

def run_coordinate_tool():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tool Đo Tọa Độ 1 Chiều - Kéo thả tạo mũi tên & Di chuyển nút")
    
    try:
        font = pygame.font.SysFont("Arial", 12, bold=True)
    except Exception:
        font = pygame.font.Font(None, 18)

    try:
        img = pygame.image.load("map.png").convert()
        img = pygame.transform.scale(img, (MAP_WIDTH, HEIGHT))
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể tải ảnh map.png ({e}). Sử dụng nền tạm thời.")
        img = pygame.Surface((MAP_WIDTH, HEIGHT))
        img.fill((40, 40, 40))

    print("\n" + "="*50)
    print("HƯỚNG DẪN SỬ DỤNG TOOL:")
    print("- Click chuột trái vào chỗ trống: Thêm điểm mới (Bắt đầu từ N1).")
    print("- KÉO CHUỘT TRÁI từ nút này sang nút khác: Tạo đường mũi tên 1 chiều.")
    print("- NHẤN GIỮ CHUỘT PHẢI VÀO NÚT: Kéo thả để DI CHUYỂN vị trí nút.")
    print("- Click chuột trái vào nút (Không kéo): Xóa nút đó.")
    print("- Click vào mũi tên màu xanh: Xóa đường nối đó.")
    print("- Nhấn phím ESC để thoát.")
    print("="*50 + "\n")
    
    initial_nodes = {
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

    initial_edges = [
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

    clicked_nodes = [{'id': int(k[1:]), 'pos': v} for k, v in initial_nodes.items()]
    custom_edges = [(int(e[0][1:]), int(e[1][1:])) for e in initial_edges]
    
    dragging_edge_node = None  
    moving_node = None         
    mouse_pos = (0, 0)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        if moving_node and mouse_pos[0] <= MAP_WIDTH:
            moving_node['pos'] = mouse_pos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x <= MAP_WIDTH:
                    if event.button == 1:
                        for node in clicked_nodes:
                            if get_distance((x, y), node['pos']) <= CLICK_RADIUS:
                                dragging_edge_node = node
                                break
                    elif event.button == 3:
                        for node in clicked_nodes:
                            if get_distance((x, y), node['pos']) <= CLICK_RADIUS:
                                moving_node = node
                                break
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if x <= MAP_WIDTH:
                    if event.button == 1:
                        if dragging_edge_node:
                            released_on_node = None
                            for node in clicked_nodes:
                                if node != dragging_edge_node and get_distance((x, y), node['pos']) <= CLICK_RADIUS:
                                    released_on_node = node
                                    break
                            
                            if released_on_node:
                                id_a = dragging_edge_node['id']
                                id_b = released_on_node['id']
                                if not any((e[0] == id_a and e[1] == id_b) for e in custom_edges):
                                    custom_edges.append((id_a, id_b))
                            else:
                                if get_distance((x, y), dragging_edge_node['pos']) <= CLICK_RADIUS:
                                    custom_edges = [e for e in custom_edges if e[0] != dragging_edge_node['id'] and e[1] != dragging_edge_node['id']]
                                    clicked_nodes.remove(dragging_edge_node)
                            
                            dragging_edge_node = None
                            print_output(clicked_nodes, custom_edges)
                            
                        else:
                            clicked_existing_edge = False
                            for edge in list(custom_edges):
                                node_a = next((n for n in clicked_nodes if n['id'] == edge[0]), None)
                                node_b = next((n for n in clicked_nodes if n['id'] == edge[1]), None)
                                if node_a and node_b:
                                    dist = get_dist_to_segment((x, y), node_a['pos'], node_b['pos'])
                                    if dist <= 6:
                                        custom_edges.remove(edge)
                                        clicked_existing_edge = True
                                        break
                            
                            if not clicked_existing_edge:
                                if clicked_nodes:
                                    new_id = max(node['id'] for node in clicked_nodes) + 1
                                    old_id = clicked_nodes[-1]['id']
                                    custom_edges.append((old_id, new_id))
                                else:
                                    new_id = 1
                                
                                clicked_nodes.append({'id': new_id, 'pos': (x, y)})
                            
                            print_output(clicked_nodes, custom_edges)

                    elif event.button == 3:
                        if moving_node:
                            moving_node = None
                            print_output(clicked_nodes, custom_edges)

        screen.blit(img, (0, 0))

        for edge in custom_edges:
            node_a = next((n for n in clicked_nodes if n['id'] == edge[0]), None)
            node_b = next((n for n in clicked_nodes if n['id'] == edge[1]), None)
            if node_a and node_b:
                draw_arrow(screen, ARROW_COLOR, node_a['pos'], node_b['pos'], arrow_size=8)

        if dragging_edge_node:
            pygame.draw.line(screen, (255, 255, 0), dragging_edge_node['pos'], mouse_pos, 1)

        for node in clicked_nodes:
            nx, ny = node['pos']
            label = f"N{node['id']}"
            
            color = (0, 255, 0) if node == moving_node else (255, 0, 0)
            
            pygame.draw.circle(screen, color, (nx, ny), NODE_RADIUS)
            pygame.draw.circle(screen, (255, 255, 255), (nx, ny), NODE_RADIUS, 1)
            
            text_surf = font.render(label, True, (255, 255, 0))
            text_rect = text_surf.get_rect(center=(nx, ny - 10))
            
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(text_surf, text_rect)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_coordinate_tool()