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
        """Vẽ các hòn đá vật cản mỹ thuật kiến trúc đa giác 3D lên tọa độ đường bị chặn"""
        for obs_id, obs in broken_edges.items():
            bx, by = int(obs['pos'][0]), int(obs['pos'][1])
            
            # 1. Vẽ bóng đổ hòn đá dưới mặt đường (Màu đen mờ thấu quang)
            shadow_surface = pygame.Surface((40, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (20, 20, 20, 130), (0, 0, 40, 24))
            self.screen.blit(shadow_surface, (bx - 20, by - 8))
            
            # 2. Định nghĩa cấu trúc các mảng khối tạo hòn đá góc cạnh mỹ thuật (3D Rock)
            # Khối chính (Thân đá xám đậm)
            pts_main = [(bx-14, by-2), (bx-6, by-15), (bx+8, by-17), (bx+16, by-4), (bx+10, by+10), (bx-10, by+8)]
            pygame.draw.polygon(self.screen, (108, 114, 123), pts_main)
            
            # Mảng khối tối khuất ánh sáng (Phía dưới và bên phải)
            pts_dark = [(bx-10, by+8), (bx+10, by+10), (bx+16, by-4), (bx+4, by+2), (bx-2, by-1)]
            pygame.draw.polygon(self.screen, (75, 80, 89), pts_dark)
            
            # Mảng khối highlight đón nắng từ góc trên bên trái (Màu xám sáng)
            pts_light = [(bx-14, by-2), (bx-6, by-15), (bx+8, by-17), (bx+2, by-8), (bx-6, by-5)]
            pygame.draw.polygon(self.screen, (148, 155, 165), pts_light)
            
            # Vẽ đường gân nứt góc cạnh sắc nét bao quanh và xuyên dọc hòn đá
            pygame.draw.polygon(self.screen, (45, 48, 53), pts_main, 2)
            pygame.draw.line(self.screen, (45, 48, 53), (bx-6, by-15), (bx-2, by-1), 2)
            pygame.draw.line(self.screen, (45, 48, 53), (bx+8, by-17), (bx+4, by+2), 2)

    def draw_vehicles(self, vehicles, graph, focused_v, show_fog, reachable_nodes):
        for v in vehicles:
            if v.state == "IDLE_IN_DEPOT": continue
            if not v.target_node_id and v.state != "STUCK_AT_OBSTACLE": continue
            if show_fog and (v.current_edge_start_id not in reachable_nodes) and (v.target_node_id not in reachable_nodes): continue
            
            vx, vy, angle = v.x, v.y, v.angle
            is_tx = v.v_id.startswith('TX_')
            L, W = (32, 16) if is_tx else (22, 11)
            
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

        # Hàng 2: Đổi màu nút Vật cản thành đỏ khi đang kích hoạt chế độ đặt vật cản
        if 'reset' in ui_rects:
            self._draw_btn(ui_rects['reset'], "Reset", (52, 152, 219))
        if 'obstacle' in ui_rects:
            obs_btn_color = (231, 76, 60) if obs_mode_on else (149, 165, 166)
            self._draw_btn(ui_rects['obstacle'], "Vật cản", obs_btn_color)

        for i in range(1, 4):
            color = (52, 152, 219) if active_map == i else (50, 50, 50)
            self._draw_btn(ui_rects[f'map{i}'], f"Kịch bản MAP {i}", color)

        for i in range(1, 7):
            color = (241, 196, 15) if active_group == i else (60, 60, 60)
            algo_name = algos[i][group_idx[i]]
            self._draw_btn(ui_rects[f'grp{i}'], f"N{i}: {algo_name}", color, use_small=True)


        if metrics.get('status_msg'):
            self.screen.blit(self.bold_font.render(metrics['status_msg'], True, metrics.get('status_color', (255,255,255))), (MAP_WIDTH + 20, 415))

        self.screen.blit(self.bold_font.render("Log Trạng Thái Phân Công", True, (200, 200, 255)), (MAP_WIDTH + 20, 445))
        y_offset = 470
        for msg in log_messages[-3:]:
            color = (255, 255, 255)
            if "CẢNH BÁO" in msg or "KẸT" in msg or "SỰ CỐ" in msg or "VI PHẠM" in msg: color = (255, 100, 100)
            elif "Đã phân công" in msg or "Hoàn thành" in msg or "THÀNH CÔNG" in msg: color = (100, 255, 100)
            elif "A*" in msg or "BFS" in msg or "CSP" in msg or "Local Search" in msg: color = (241, 196, 15)
            self.screen.blit(self.font.render(msg, True, color), (MAP_WIDTH + 20, y_offset))
            y_offset += 24

    def _draw_btn(self, rect, text, color, use_small=False):
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, (255,255,255), rect, width=2, border_radius=6)
        fnt = self.font if use_small else self.bold_font
        txt = fnt.render(text, True, (0, 0, 0) if color[0] > 200 or color == (46, 204, 113) else (255,255,255))
        self.screen.blit(txt, (rect.centerx - txt.get_width() / 2, rect.centery - txt.get_height() / 2))