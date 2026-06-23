import pygame
import math
from config import *

class Renderer:
    def __init__(self, screen, font, bold_font, title_font):
        self.screen = screen
        self.font = font
        self.bold_font = bold_font
        self.title_font = title_font

    def draw_graph(self, graph, broken_edges, customers, reachable_edges, show_fog):
        """Vẽ các hòn đá vật cản và khách hàng kèm hiệu ứng thu phóng lên bản đồ"""
        # --- LÝ TRÌNH VẼ VẬT CẢN HÒN ĐÁ 3D ---
        for obs_id, obs in broken_edges.items():
            bx, by = int(obs['pos'][0]), int(obs['pos'][1])
            shadow_surface = pygame.Surface((40, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (20, 20, 20, 130), (0, 0, 40, 24))
            self.screen.blit(shadow_surface, (bx - 20, by - 8))
            
            pts_main = [(bx-14, by-2), (bx-6, by-15), (bx+8, by-17), (bx+16, by-4), (bx+10, by+10), (bx-10, by+8)]
            pygame.draw.polygon(self.screen, (108, 114, 123), pts_main)
            
            pts_dark = [(bx-10, by+8), (bx+10, by+10), (bx+16, by-4), (bx+4, by+2), (bx-2, by-1)]
            pygame.draw.polygon(self.screen, (75, 80, 89), pts_dark)
            
            pts_light = [(bx-14, by-2), (bx-6, by-15), (bx+8, by-17), (bx+2, by-8), (bx-6, by-5)]
            pygame.draw.polygon(self.screen, (148, 155, 165), pts_light)
            
            pygame.draw.polygon(self.screen, (45, 48, 53), pts_main, 2)
            pygame.draw.line(self.screen, (45, 48, 53), (bx-6, by-15), (bx-2, by-1), 2)
            pygame.draw.line(self.screen, (45, 48, 53), (bx+8, by-17), (bx+4, by+2), 2)

        # --- LÝ TRÌNH VẼ KHÁCH HÀNG CHẤM TRÒN THU PHÓNG ---
        current_time = pygame.time.get_ticks()
        # Tạo hiệu ứng xung số từ 0.0 đến 1.0 thay đổi liên tục theo thời gian
        pulse_factor = (math.sin(current_time * 0.007) + 1.0) / 2.0  
        
        for cust in customers:
            if cust['start'] in graph.nodes:
                node = graph.nodes[cust['start']]
                cx, cy = node.x, node.y
                
                # Bán kính vòng tròn hiệu ứng bên ngoài co giãn từ 8 đến 16 pixel
                outer_radius = int(8 + pulse_factor * 8)
                
                # Vẽ vòng tròn mờ lan tỏa phía dưới (Hiệu ứng sóng radar)
                glow_surf = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (46, 204, 113, 80), (outer_radius, outer_radius), outer_radius)
                self.screen.blit(glow_surf, (cx - outer_radius, cy - outer_radius))
                
                # Vẽ chấm tròn lõi cứng định vị ở tâm màu xanh lục sáng
                pygame.draw.circle(self.screen, (46, 204, 113), (cx, cy), 6)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 6, 1) # Viền trắng mảnh

    def draw_vehicles(self, vehicles, graph, focused_v, show_fog, reachable_nodes):
        for v in vehicles:
            if v.state == "IDLE_IN_DEPOT": continue
            if not v.target_node_id and v.state != "STUCK_AT_OBSTACLE": continue
            if show_fog and (v.current_edge_start_id not in reachable_nodes) and (v.target_node_id not in reachable_nodes): continue
            
            vx, vy, angle = v.x, v.y, v.angle
            is_tx = v.v_id.startswith('TX_')
            L, W = (32, 16) if is_tx else (22, 11)
            
            # Gán màu nguyên bản của xe, loại bỏ hoàn toàn logic đổi màu trắng khi nhấp chọn xe (focus)
            if is_tx: body_c = (245, 185, 15)
            elif hasattr(v, 'color'): body_c = v.color
            else: body_c = (189, 195, 199)
            
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            def get_pt(dx, dy): return (vx + dx * cos_a - dy * sin_a, vy + dx * sin_a + dy * cos_a)
            
            wl, ww = L * 0.25, 3
            wdx, wdy = L * 0.3, W/2 + 1
            for dx, dy in [(wdx, wdy), (wdx, -wdy), (-wdx, wdy), (-wdx, -wdy)]:
                pygame.draw.polygon(self.screen, (20, 20, 20), [get_pt(dx + wl/2, dy + ww/2), get_pt(dx - wl/2, dy + ww/2), get_pt(dx - wl/2, dy - ww/2), get_pt(dx + wl/2, dy - ww/2)])
            
            pts = [get_pt(L/2, W/2), get_pt(-L/2, W/2), get_pt(-L/2, -W/2), get_pt(L/2, -W/2)]
            pygame.draw.polygon(self.screen, body_c, pts)
            pygame.draw.polygon(self.screen, (30, 30, 30), pts, 1)
            
            fw_pts = [get_pt(L/2 - 3, W/2 - 1.5), get_pt(L/4, W/2 - 1.5), get_pt(L/4, -W/2 + 1.5), get_pt(L/2 - 3, -W/2 + 1.5)]
            pygame.draw.polygon(self.screen, (30, 35, 40), fw_pts)
            
            rw_pts = [get_pt(-L/2 + 2, W/2 - 1.5), get_pt(-L/4 - 1, W/2 - 1.5), get_pt(-L/4 - 1, -W/2 + 1.5), get_pt(-L/2 + 2, -W/2 + 1.5)]
            pygame.draw.polygon(self.screen, (30, 35, 40), rw_pts)
            
            roof_pts = [get_pt(L/4, W/2 - 1.5), get_pt(-L/4 - 1, W/2 - 1.5), get_pt(-L/4 - 1, -W/2 + 1.5), get_pt(L/4, -W/2 + 1.5)]
            rc = (max(0, body_c[0]-40), max(0, body_c[1]-40), max(0, body_c[2]-40))
            pygame.draw.polygon(self.screen, rc, roof_pts)
            
            pygame.draw.circle(self.screen, (255, 255, 200), (int(get_pt(L/2, W/2 - 2)[0]), int(get_pt(L/2, W/2 - 2)[1])), 2)
            pygame.draw.circle(self.screen, (255, 255, 200), (int(get_pt(L/2, -W/2 + 2)[0]), int(get_pt(L/2, -W/2 + 2)[1])), 2)
            pygame.draw.circle(self.screen, (255, 50, 50), (int(get_pt(-L/2, W/2 - 2)[0]), int(get_pt(-L/2, W/2 - 2)[1])), 2)
            pygame.draw.circle(self.screen, (255, 50, 50), (int(get_pt(-L/2, -W/2 + 2)[0]), int(get_pt(-L/2, -W/2 + 2)[1])), 2)
            
            if is_tx:
                pygame.draw.rect(self.screen, (20, 20, 20), (vx - 4, vy - 2.5, 8, 5))
                pygame.draw.rect(self.screen, (245, 185, 15), (vx - 3, vy - 1.5, 6, 3))
                
                parts = v.v_id.split("_")
                display_id = f"{parts[2]}_{parts[1]}" if len(parts) >= 3 else v.v_id
                
                lbl = self.bold_font.render(display_id, True, (241, 196, 15))
                self.screen.blit(lbl, (vx - lbl.get_width() / 2, vy - 28))
            
            # ĐÃ XÓA logic vẽ các chuỗi text trạng thái phụ ("DỪNG", "BỊ CHẶN") trên đầu xe

    def draw_dashboard(self, log_messages, ui_rects, is_paused, select_mode, show_fog):
        pygame.draw.rect(self.screen, COLOR_DASHBOARD, (MAP_WIDTH, 0, DASHBOARD_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, (70, 70, 80), (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 4)

        sync_data = ui_rects.get('_state_sync', {})
        active_map = sync_data.get('active_map', 1)
        active_group = sync_data.get('active_group', None)
        group_idx = sync_data.get('group_idx', {i: 0 for i in range(1, 7)})
        algos = sync_data.get('algos', {i: [""]*3 for i in range(1, 7)})
        metrics = sync_data.get('metrics', {})
        obs_mode_on = sync_data.get('obstacle_mode', False)

        # Hàng 1
        self._draw_btn(ui_rects['start'], "Bắt đầu", (46, 204, 113))
        self._draw_btn(ui_rects['stop'], "Dừng", (231, 76, 60))

        # Hàng 2: Reset & Vật cản
        if 'reset' in ui_rects:
            self._draw_btn(ui_rects['reset'], "Reset", (52, 152, 219))
        if 'obstacle' in ui_rects:
            obs_btn_color = (231, 76, 60) if obs_mode_on else (149, 165, 166)
            self._draw_btn(ui_rects['obstacle'], "Vật cản", obs_btn_color)

        # Hàng 3: Kịch bản MAP dọc
        for i in range(1, 4):
            color = (52, 152, 219) if active_map == i else (50, 50, 50)
            self._draw_btn(ui_rects[f'map{i}'], f"Kịch bản MAP {i}", color)

        # Hàng 4: 6 nhóm thuật toán Panel Panel
        for i in range(1, 7):
            color = (241, 196, 15) if active_group == i else (60, 60, 60)
            algo_name = algos[i][group_idx[i]]
            self._draw_btn(ui_rects[f'grp{i}'], f"N{i}: {algo_name}", color, use_small=True)

        # BẢNG SO SÁNH HIỆU NĂNG REAL-TIME (Tọa độ Y được căn xuống 385 tránh va chạm đè chữ)
        self.screen.blit(self.title_font.render("SO SÁNH HIỆU NĂNG", True, (241, 196, 15)), (MAP_WIDTH + 20, 385))
        
        # Tiêu đề cột
        self.screen.blit(self.bold_font.render("Thuật toán", True, (200, 200, 200)), (MAP_WIDTH + 20, 420))
        self.screen.blit(self.bold_font.render("Quãng đường", True, (200, 200, 200)), (MAP_WIDTH + 115, 420))
        self.screen.blit(self.bold_font.render("Doanh thu", True, (200, 200, 200)), (MAP_WIDTH + 210, 420))
        
        # Đường gạch chân tiêu đề
        pygame.draw.line(self.screen, (100, 100, 110), (MAP_WIDTH + 20, 440), (MAP_WIDTH + DASHBOARD_WIDTH - 20, 440), 1)

        leaderboard = metrics.get('taxi_leaderboard', {})
        y_row = 450
        
        for name, data in leaderboard.items():
            # Cột 1: Tên thuật toán định dạng (Ví dụ: BFS_1)
            self.screen.blit(self.font.render(name, True, (255, 255, 255)), (MAP_WIDTH + 20, y_row))
            # Cột 2: Quãng đường thực xe chạy tích lũy từ vị trí (px)
            self.screen.blit(self.font.render(f"{data['distance']} px", True, (255, 255, 255)), (MAP_WIDTH + 115, y_row))
            # Cột 3: Doanh thu thực tế của xe
            self.screen.blit(self.font.render(f"{data['revenue']:,}đ", True, (46, 204, 113)), (MAP_WIDTH + 210, y_row))
            
            y_row += 24

    def _draw_btn(self, rect, text, color, use_small=False):
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, (255,255,255), rect, width=2, border_radius=6)
        fnt = self.font if use_small else self.bold_font
        txt = fnt.render(text, True, (0, 0, 0) if color[0] > 200 or color == (46, 204, 113) else (255,255,255))
        self.screen.blit(txt, (rect.centerx - txt.get_width() / 2, rect.centery - txt.get_height() / 2))

    def draw_focused_vehicle_ui(self, vehicle):
        pass