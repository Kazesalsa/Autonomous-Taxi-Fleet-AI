import pygame
import math
from config import *

class Renderer:
    def __init__(self, screen, font, bold_font, title_font):
        self.screen = screen
        self.font = font
        self.bold_font = bold_font
        self.title_font = title_font

    def draw_depot(self, graph):
        gate = graph.nodes['GATE']
        rect = pygame.Rect(gate.x - 160, gate.y - 120, 200, 100)
        pygame.draw.rect(self.screen, COLOR_DEPOT, rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ROAD_LINE, rect, width=4, border_radius=8)
        
        lbl = self.bold_font.render("DEPOT - BÃI XE", True, (255, 255, 255))
        self.screen.blit(lbl, (rect.x + 10, rect.y + 10))
        
        # Draw slots
        for p_id in ['P1','P2','P3','P4','P5','P6','P7','P8']:
            n = graph.nodes[p_id]
            pygame.draw.rect(self.screen, (60, 80, 100), (n.x - 15, n.y - 10, 30, 20), width=2)

    def draw_graph(self, graph, broken_edges, customers):
        self.draw_depot(graph)

        drawn_edges = set()
        for node_id, node in graph.nodes.items():
            if 'P' in node_id or node_id == 'DEPOT': continue # Skip drawing lines inside depot area
            
            for edge in node.edges:
                target = graph.nodes[edge.target_id]
                edge_id = tuple(sorted((node_id, edge.target_id)))
                if edge_id in drawn_edges: continue
                drawn_edges.add(edge_id)

                pygame.draw.line(self.screen, COLOR_ROAD, (node.x, node.y), (target.x, target.y), ROAD_WIDTH)
                
                dir_x = target.x - node.x
                dir_y = target.y - node.y
                length = math.hypot(dir_x, dir_y)
                if length > 0 and edge_id not in broken_edges:
                    nx, ny = dir_x / length, dir_y / length
                    for i in range(30, int(length) - 30, 40):
                        pygame.draw.line(self.screen, COLOR_ROAD_LINE, (node.x + i * nx, node.y + i * ny), (node.x + (i+20) * nx, node.y + (i+20) * ny), 2)
                
        # Draw events on edges
        for edge_id, obs_data in broken_edges.items():
            ox, oy = obs_data['pos']
            otype = obs_data['type']
            
            if otype == 'CROSSWALK':
                nx, ny = obs_data['dir']
                px, py = -ny, nx
                for i in range(-15, 20, 8):
                    sx = ox + px * i - nx * 10
                    sy = oy + py * i - ny * 10
                    ex = ox + px * i + nx * 10
                    ey = oy + py * i + ny * 10
                    pygame.draw.line(self.screen, (255, 255, 255), (sx, sy), (ex, ey), 4)
                # Vẽ người nhỏ
                pygame.draw.circle(self.screen, (46, 204, 113), (int(ox), int(oy)), 6)
                pygame.draw.circle(self.screen, (46, 204, 113), (int(ox+10), int(oy+5)), 6)

            elif otype == 'ROCK':
                pygame.draw.circle(self.screen, (100, 100, 100), (int(ox), int(oy)), 16)
                pygame.draw.circle(self.screen, (140, 140, 140), (int(ox-4), int(oy-4)), 5)
            elif otype == 'LOG':
                pts = self._get_rotated_points(ox, oy, 14, 36, math.pi/4)
                pygame.draw.polygon(self.screen, (139, 69, 19), pts)
                pygame.draw.polygon(self.screen, (101, 67, 33), pts, 2)

        for node_id, node in graph.nodes.items():
            if 'P' in node_id or node_id == 'DEPOT': continue

            pygame.draw.circle(self.screen, COLOR_ROAD, (int(node.x), int(node.y)), int(ROAD_WIDTH/2))
            
            if node.has_light:
                if node.csp_locked: pygame.draw.circle(self.screen, COLOR_AMBULANCE, (int(node.x), int(node.y)), int(ROAD_WIDTH/2 + 8), 3)

                time_sec = math.ceil(node.light_timer / 60)
                text = self.bold_font.render(str(time_sec), True, (255, 255, 255))
                pygame.draw.rect(self.screen, (40, 40, 40), (node.x - 12, node.y - 12, 24, 24), border_radius=4)
                self.screen.blit(text, (node.x - text.get_width() / 2, node.y - text.get_height() / 2))

                for edge in node.edges:
                    t = graph.nodes[edge.target_id]
                    dx, dy = node.x - t.x, node.y - t.y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        axis = 'H' if abs(dx) > abs(dy) else 'V'
                        lc_str = 'RED'
                        if axis == 'H': lc_str = 'GREEN' if node.light_state == 'H_GREEN' else ('YELLOW' if node.light_state == 'H_YELLOW' else 'RED')
                        else: lc_str = 'GREEN' if node.light_state == 'V_GREEN' else ('YELLOW' if node.light_state == 'V_YELLOW' else 'RED')
                        
                        lc = (46, 204, 113) if lc_str == 'GREEN' else ((241, 196, 15) if lc_str == 'YELLOW' else (231, 76, 60))
                        
                        nx, ny = dx/dist, dy/dist
                        px, py = -ny, nx
                        sx = node.x - nx * (ROAD_WIDTH/2 + 5) + px * (ROAD_WIDTH/2 + 5)
                        sy = node.y - ny * (ROAD_WIDTH/2 + 5) + py * (ROAD_WIDTH/2 + 5)
                        
                        pygame.draw.rect(self.screen, (50, 50, 50), (sx - 4, sy - 4, 8, 8), border_radius=2)
                        pygame.draw.circle(self.screen, lc, (int(sx), int(sy)), 4)
            else:
                lbl = self.font.render(node_id, True, (120, 120, 120))
                self.screen.blit(lbl, (node.x + int(ROAD_WIDTH/2), node.y - 10))

        # Vẽ Khách Hàng
        for c in customers:
            sn = graph.nodes[c['start']]
            gn = graph.nodes[c['goal']]
            if c['status'] == 'WAITING':
                pygame.draw.circle(self.screen, COLOR_CUSTOMER, (int(sn.x), int(sn.y)), 12)
                pygame.draw.circle(self.screen, (255,255,255), (int(sn.x), int(sn.y)), 12, 2)
                self.screen.blit(self.bold_font.render("KH", True, (0,0,0)), (sn.x - 10, sn.y - 10))
                
                pygame.draw.circle(self.screen, COLOR_DESTINATION, (int(gn.x), int(gn.y)), 10, 2)
                pygame.draw.circle(self.screen, COLOR_DESTINATION, (int(gn.x), int(gn.y)), 4)

    def draw_vehicles(self, vehicles, graph, focused_v):
        for v in vehicles:
            if v.state == "IDLE_IN_DEPOT":
                n = graph.nodes[v.current_node_id]
                pygame.draw.rect(self.screen, COLOR_TAXI, (n.x - 12, n.y - 8, 24, 16))
                pygame.draw.rect(self.screen, (0,0,0), (n.x - 12, n.y - 8, 24, 16), 2)
                continue

            if not v.target_node_id and v.state != "STUCK_AT_OBSTACLE": continue

            base_offset = 4 if v.is_ambulance else LANE_OFFSETS[v.lane]
            offset = base_offset + v.pull_over_offset
            vx = v.x + math.cos(v.angle + math.pi/2) * offset
            vy = v.y + math.sin(v.angle + math.pi/2) * offset

            size = (26, 14) if v.is_ambulance else (22, 12)
            pts = self._get_rotated_points(vx, vy, size[0], size[1], v.angle)
            
            if v == focused_v: color = (255, 255, 255)
            elif v.is_ambulance: color = COLOR_AMBULANCE
            elif v.status in ["CARRYING", "TO_CUSTOMER"]: color = COLOR_TAXI_BUSY
            else: color = COLOR_TAXI
            
            pygame.draw.polygon(self.screen, color, pts)
            
            if v.is_ambulance:
                pygame.draw.line(self.screen, (255,255,255), (vx - 6, vy), (vx + 6, vy), 3)
                pygame.draw.line(self.screen, (255,255,255), (vx, vy - 6), (vx, vy + 6), 3)
            else:
                # Dấu hiệu Taxi
                pygame.draw.rect(self.screen, (0,0,0), (vx - 4, vy - 2, 8, 4))
                pygame.draw.circle(self.screen, (0, 0, 0), (int(vx + math.cos(v.angle)*5), int(vy + math.sin(v.angle)*5)), 2)

            if v.state in ["YIELD", "SAFE_WAIT"]:
                text = self.bold_font.render("DỪNG", True, (255, 100, 100))
                self.screen.blit(text, (vx - 20, vy - 25))

    def _get_rotated_points(self, x, y, width, height, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return [(x + pt[0]*cos_a - pt[1]*sin_a, y + pt[0]*sin_a + pt[1]*cos_a) for pt in [(-width/2, -height/2), (width/2, -height/2), (width/2, height/2), (-width/2, height/2)]]

    def draw_dashboard(self, log_messages, ui_rects, is_paused, select_mode):
        pygame.draw.rect(self.screen, COLOR_DASHBOARD, (MAP_WIDTH, 0, DASHBOARD_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, (70, 70, 80), (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 4)

        self.screen.blit(self.title_font.render("TAXI FLEET AI MANAGER", True, (255, 255, 255)), (MAP_WIDTH + 20, 20))
        
        self._draw_btn(ui_rects['pause'], "► Tiếp Tục Thời Gian" if is_paused else "|| Dừng Thời Gian", (231, 76, 60) if is_paused else (46, 204, 113))

        self.screen.blit(self.bold_font.render("Nghiệp Vụ Đón Khách", True, (200, 200, 255)), (MAP_WIDTH + 20, 150))
        self._draw_btn(ui_rects['customer'], "Tạo Khách Hàng Gọi Xe", (46, 204, 113) if not select_mode.startswith('CUST') else (241, 196, 15))

        self.screen.blit(self.bold_font.render("Tạo Sự Kiện (Click Map)", True, (200, 200, 255)), (MAP_WIDTH + 20, 260))
        self._draw_btn(ui_rects['crosswalk'], "1. Người Băng Qua Đường", (52, 152, 219) if select_mode != 'CROSS' else (241, 196, 15))
        self._draw_btn(ui_rects['obstacle'], "2. Tạo Tai Nạn / Vật Cản", (231, 76, 60) if select_mode != 'OBS' else (241, 196, 15))
        self._draw_btn(ui_rects['ambulance'], "3. Xe Cấp Cứu Ưu Tiên", (155, 89, 182) if select_mode != 'AMB' else (241, 196, 15))

        if select_mode:
            info = "CLICK ĐỂ THỰC HIỆN..."
            if select_mode == 'CUST_START': info = "B1: CLICK CHỌN ĐIỂM ĐÓN KHÁCH"
            elif select_mode == 'CUST_GOAL': info = "B2: CLICK CHỌN ĐIỂM TRẢ KHÁCH"
            elif select_mode == 'CROSS': info = "CLICK VÀO ĐOẠN ĐƯỜNG BẤT KỲ"
            self.screen.blit(self.bold_font.render(info, True, (241, 196, 15)), (MAP_WIDTH + 20, 420))

        self.screen.blit(self.bold_font.render("Log Trạng Thái Phân Công", True, (200, 200, 255)), (MAP_WIDTH + 20, 480))
        y_offset = 510
        for msg in log_messages[-15:]:
            color = (255, 255, 255)
            if "CẢNH BÁO" in msg or "KẸT" in msg: color = (255, 100, 100)
            elif "Đã phân công" in msg or "Hoàn thành" in msg: color = (100, 255, 100)
            elif "A*" in msg or "BFS" in msg or "CSP" in msg or "ONLINE" in msg: color = (241, 196, 15)
            self.screen.blit(self.font.render(msg, True, color), (MAP_WIDTH + 20, y_offset))
            y_offset += 24

    def _draw_btn(self, rect, text, color):
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, (255,255,255), rect, width=2, border_radius=6)
        txt = self.bold_font.render(text, True, (0, 0, 0) if color[0] > 200 else (255,255,255))
        self.screen.blit(txt, (rect.centerx - txt.get_width() / 2, rect.centery - txt.get_height() / 2))
