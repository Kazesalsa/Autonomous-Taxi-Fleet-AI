import pygame
import sys
import os
import math

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    from config import WIDTH, HEIGHT, MAP_WIDTH
except ImportError:
    WIDTH, HEIGHT, MAP_WIDTH = 918, 865, 918 

# Thông số cấu hình hiển thị
NODE_RADIUS = 4
CLICK_RADIUS = 8
ARROW_COLOR = (0, 191, 255) # Màu xanh dương sáng

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
    """Hàm hỗ trợ vẽ đường nối có mũi tên (1 chiều)"""
    pygame.draw.line(screen, color, start, end, 2)
    
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    end_adj = (end[0] - NODE_RADIUS * math.cos(angle), end[1] - NODE_RADIUS * math.sin(angle))
    
    angle_left = angle - math.pi / 6  
    angle_right = angle + math.pi / 6 
    
    p1 = (end_adj[0] - arrow_size * math.cos(angle_left), end_adj[1] - arrow_size * math.sin(angle_left))
    p2 = (end_adj[0] - arrow_size * math.cos(angle_right), end_adj[1] - arrow_size * math.sin(angle_right))
    
    pygame.draw.polygon(screen, color, [end_adj, p1, p2])

def print_output(clicked_nodes, custom_edges):
    """In kết quả ra màn hình Console Terminal"""
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

    clicked_nodes = [] 
    custom_edges = []  
    
    dragging_edge_node = None  # Phục vụ kéo đường nối bằng chuột trái
    moving_node = None         # Phục vụ kéo di chuyển nút bằng chuột phải
    mouse_pos = (0, 0)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Nếu đang kéo di chuyển nút bằng chuột phải
        if moving_node and mouse_pos[0] <= MAP_WIDTH:
            moving_node['pos'] = mouse_pos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                
            # --- XỬ LÝ CLICK CHUỘT XUỐNG ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x <= MAP_WIDTH:
                    # Chuột trái (Button 1): Bắt đầu kéo nối đường hoặc click nút
                    if event.button == 1:
                        for node in clicked_nodes:
                            if get_distance((x, y), node['pos']) <= CLICK_RADIUS:
                                dragging_edge_node = node
                                break
                    # Chuột phải (Button 3): Kích hoạt chế độ di chuyển nút
                    elif event.button == 3:
                        for node in clicked_nodes:
                            if get_distance((x, y), node['pos']) <= CLICK_RADIUS:
                                moving_node = node
                                break
                            
            # --- XỬ LÝ THẢ CHUỘT RA ---
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if x <= MAP_WIDTH:
                    # Thả chuột trái (Logic nối hoặc xóa đường/nút)
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

                    # Thả chuột phải (Hoàn tất hành động di chuyển nút)
                    elif event.button == 3:
                        if moving_node:
                            moving_node = None
                            print_output(clicked_nodes, custom_edges)

        # --- BẮT ĐẦU VẼ GIAO DIỆN ---
        screen.blit(img, (0, 0))

        # Vẽ đường nối có mũi tên (1 chiều)
        for edge in custom_edges:
            node_a = next((n for n in clicked_nodes if n['id'] == edge[0]), None)
            node_b = next((n for n in clicked_nodes if n['id'] == edge[1]), None)
            if node_a and node_b:
                draw_arrow(screen, ARROW_COLOR, node_a['pos'], node_b['pos'], arrow_size=8)

        # Vẽ nét kéo nháp bằng chuột trái
        if dragging_edge_node:
            pygame.draw.line(screen, (255, 255, 0), dragging_edge_node['pos'], mouse_pos, 1)

        # Vẽ các nút nhỏ và nhãn tên
        for node in clicked_nodes:
            nx, ny = node['pos']
            label = f"N{node['id']}"
            
            # Đổi sang màu xanh lá cây khi nút đang được kéo di chuyển bằng chuột phải
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