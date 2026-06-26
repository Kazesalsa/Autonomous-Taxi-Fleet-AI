import pygame
import math
from config import *

class Renderer:
    def __init__(self, screen, font, bold_font, title_font):
        self.screen = screen
        self.font = font
        self.bold_font = bold_font
        self.title_font = title_font

    def draw_graph(self, graph, broken_edges, customers, reachable_edges, show_fog, pending_spawn_nodes=None, focused_vehicle=None, traffic_light_colors=None):
        """Vẽ các hòn đá vật cản, khách hàng kèm hiệu ứng thu phóng và hệ thống đèn giao thông lên bản đồ"""
        
        # --- VẼ ĐƯỜNG LỘ TRÌNH CHO XE ĐƯỢC CHỌN (FOCUS) ---
        if focused_vehicle:
            path_pts = [(focused_vehicle.x, focused_vehicle.y)]
            if focused_vehicle.target_node_id in graph.nodes:
                n = graph.nodes[focused_vehicle.target_node_id]
                path_pts.append((n.x, n.y))
            for n_id in focused_vehicle.path:
                if n_id in graph.nodes:
                    n = graph.nodes[n_id]
                    path_pts.append((n.x, n.y))
            
            if len(path_pts) > 1:
                pygame.draw.lines(self.screen, (241, 196, 15), False, path_pts, 4) 
                pygame.draw.circle(self.screen, (241, 196, 15), (int(path_pts[-1][0]), int(path_pts[-1][1])), 8) 

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
        pulse_factor = (math.sin(current_time * 0.007) + 1.0) / 2.0  
        outer_radius = int(8 + pulse_factor * 8)
        
        for cust in customers:
            lbl_text = cust.get('label', '')
            is_patient = cust.get('is_patient', False)
            
            # VẼ ĐIỂM ĐÓN (CHỮ A) - CHỈ VẼ NẾU CHƯA ĐƯỢC ĐÓN
            if not cust.get('picked_up', False) and cust['start'] in graph.nodes:
                node = graph.nodes[cust['start']]
                cx, cy = node.x, node.y


                
                if not cust.get('agree_to_share', True):
                    glow_color = (241, 196, 15, 80) 
                    core_color = (241, 196, 15) 
                elif is_patient:
                    glow_color = (155, 89, 182, 80) # Purple for patient
                    core_color = (155, 89, 182)
                else:
                    glow_color = (46, 204, 113, 80) 
                    core_color = (46, 204, 113) 
                
                glow_surf = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color, (outer_radius, outer_radius), outer_radius)
                self.screen.blit(glow_surf, (cx - outer_radius, cy - outer_radius))
                
                pygame.draw.circle(self.screen, core_color, (cx, cy), 8)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 8, 1)
                
                lbl_render = self.bold_font.render(lbl_text, True, (0, 0, 0))
                self.screen.blit(lbl_render, (cx - lbl_render.get_width()/2, cy - lbl_render.get_height()/2))

            # VẼ ĐIỂM TRẢ CHO KHÁCH (BỆNH NHÂN KHÔNG CẦN ĐIỂM TRẢ VÌ ĐÃ CÓ ĐIỂM ĐÓN)
            if not is_patient and not cust.get('delivered', False) and cust['goal'] in graph.nodes:
                node = graph.nodes[cust['goal']]
                cx, cy = node.x, node.y


                
                glow_surf = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (231, 76, 60, 80), (outer_radius, outer_radius), outer_radius)
                self.screen.blit(glow_surf, (cx - outer_radius, cy - outer_radius))
                
                pygame.draw.circle(self.screen, (231, 76, 60), (cx, cy), 8)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 8, 1)
                lbl_render_red = self.bold_font.render(lbl_text, True, (255, 255, 255))
                self.screen.blit(lbl_render_red, (cx - lbl_render_red.get_width()/2, cy - lbl_render_red.get_height()/2))

        # VẼ HIỆU ỨNG NHẤP NHÁY CHỌN ĐIỂM XUẤT PHÁT TẠI EDGE_NODES
        if pending_spawn_nodes:
            for n_id in pending_spawn_nodes:
                if n_id in graph.nodes:
                    node = graph.nodes[n_id]
                    cx, cy = node.x, node.y
                    glow_surf = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (52, 152, 219, 120), (outer_radius, outer_radius), outer_radius)
                    self.screen.blit(glow_surf, (cx - outer_radius, cy - outer_radius))
                    pygame.draw.circle(self.screen, (52, 152, 219), (cx, cy), 8)

        # --- VẼ 18 HỘP ĐÈN GIAO THÔNG VẬT LÝ ---
        if traffic_light_colors:
            for sp_id, data in traffic_light_colors.items():
                px, py = data['pos']
                color = data['color']
                
                pygame.draw.rect(self.screen, (30, 30, 30), (px - 6, py - 14, 12, 28), border_radius=3)
                pygame.draw.rect(self.screen, (100, 100, 100), (px - 6, py - 14, 12, 28), 1, border_radius=3)
                
                pygame.draw.circle(self.screen, (60, 20, 20), (px, py - 8), 3) 
                pygame.draw.circle(self.screen, (60, 60, 20), (px, py), 3)     
                pygame.draw.circle(self.screen, (20, 60, 20), (px, py + 8), 3) 
                
                if color == (231, 76, 60): 
                    pygame.draw.circle(self.screen, color, (px, py - 8), 4)
                    glow = pygame.Surface((16, 16), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (231, 76, 60, 100), (8, 8), 8)
                    self.screen.blit(glow, (px - 8, py - 16))
                elif color == (241, 196, 15): 
                    pygame.draw.circle(self.screen, color, (px, py), 4)
                    glow = pygame.Surface((16, 16), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (241, 196, 15, 100), (8, 8), 8)
                    self.screen.blit(glow, (px - 8, py - 8))
                elif color == (46, 204, 113): 
                    pygame.draw.circle(self.screen, color, (px, py + 8), 4)
                    glow = pygame.Surface((16, 16), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (46, 204, 113, 100), (8, 8), 8)
                    self.screen.blit(glow, (px - 8, py))

    def draw_vehicles(self, vehicles, graph, focused_v, show_fog, reachable_nodes):
        """Vẽ các phương tiện di chuyển trên bản đồ"""
        for v in vehicles:
            if v.state == "IDLE_IN_DEPOT": continue
            is_tx = v.v_id.startswith('TX_')
            is_amb = getattr(v, 'is_ambulance', False)
            if is_amb or is_tx:
                pass # Always draw Taxis and Ambulances unless IDLE_IN_DEPOT
            elif not v.target_node_id and v.state != "STUCK_AT_OBSTACLE": continue
            if show_fog and (v.current_edge_start_id not in reachable_nodes) and (v.target_node_id not in reachable_nodes): continue
            
            vx, vy, angle = v.x, v.y, v.angle


            is_tx = v.v_id.startswith('TX_')
            is_amb = getattr(v, 'is_ambulance', False)
            
            if is_amb: L, W = (36, 18)
            elif is_tx: L, W = (32, 16)
            else: L, W = (22, 11)
            
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
            
            if getattr(v, 'is_ambulance', False):
                # Draw a red cross on the roof
                c_x, c_y = get_pt(0, 0)
                cross_len = L/6
                pygame.draw.line(self.screen, (231, 76, 60), get_pt(cross_len, 0), get_pt(-cross_len, 0), 2)
                pygame.draw.line(self.screen, (231, 76, 60), get_pt(0, cross_len), get_pt(0, -cross_len), 2)
            
            if is_tx:
                pygame.draw.rect(self.screen, (20, 20, 20), (vx - 4, vy - 2.5, 8, 5))
                pygame.draw.rect(self.screen, (245, 185, 15), (vx - 3, vy - 1.5, 6, 3))
                
                parts = v.v_id.split("_")
                display_id = f"{parts[2]}_{parts[1]}" if len(parts) >= 3 else v.v_id
                
                lbl = self.bold_font.render(display_id, True, (241, 196, 15))
                self.screen.blit(lbl, (vx - lbl.get_width() / 2, vy - 28))


    def draw_dashboard(self, log_messages, ui_rects, is_paused, select_mode, show_fog):
        """Vẽ bảng điều khiển Dashboard bên tay phải"""
        pygame.draw.rect(self.screen, COLOR_DASHBOARD, (MAP_WIDTH, 0, DASHBOARD_WIDTH, HEIGHT))
        # Bright separator line between map and dashboard
        pygame.draw.line(self.screen, (90, 95, 110), (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 3)

        sync_data = ui_rects.get('_state_sync', {})
        active_map = sync_data.get('active_map', 1)
        active_group = sync_data.get('active_group', None)
        group_idx = sync_data.get('group_idx', {i: 0 for i in range(1, 7)})
        algos = sync_data.get('algos', {i: [""]*3 for i in range(1, 7)})
        metrics = sync_data.get('metrics', {})
        obs_mode_on = sync_data.get('obstacle_mode', False)

        # Hàng 1
        self._draw_btn(ui_rects['start'], "Bắt đầu", (46, 204, 113))
        
        # Vẽ nút Tạo (Create) - toggle giữa Khách và Bệnh nhân
        create_rect = ui_rects['create']
        create_mode = sync_data.get('create_mode', "Khách")
        
        if create_mode == "Bệnh nhân":
            btn_color = (155, 89, 182)  # Màu tím (Bệnh nhân)
            mode_text = "Bệnh nhân"
            text_color = (255, 255, 255)
        else:  # "Khách" (mặc định)
            btn_color = (46, 204, 113)  # Màu xanh lá (Khách hàng)
            mode_text = "Khách"
            text_color = (0, 0, 0)

        pygame.draw.rect(self.screen, btn_color, create_rect, border_radius=6)
        pygame.draw.rect(self.screen, (255, 255, 255), create_rect, width=2, border_radius=6)
        
        txt_create = self.bold_font.render("Tạo", True, text_color)
        self.screen.blit(txt_create, (create_rect.centerx - txt_create.get_width() / 2, create_rect.y + 4))
        
        txt_mode = self.font.render(mode_text, True, text_color)
        self.screen.blit(txt_mode, (create_rect.centerx - txt_mode.get_width() / 2, create_rect.y + 22))

        # Hàng 2: Reset & Vật cản
        if 'reset' in ui_rects:
            self._draw_btn(ui_rects['reset'], "Reset", (52, 152, 219))
        if 'obstacle' in ui_rects:
            obs_btn_color = (231, 76, 60) if obs_mode_on else (149, 165, 166)
            self._draw_btn(ui_rects['obstacle'], "Vật cản", obs_btn_color)

        # Hàng 3: Kịch bản MAP dọc
        for i in range(1, 3):
            if f'map{i}' in ui_rects:
                color = (52, 152, 219) if active_map == i else (50, 50, 50)
                self._draw_btn(ui_rects[f'map{i}'], f"Kịch bản {i}", color)

        # Hàng 4: 5 nhóm thuật toán Panel
        for i in range(1, 6):
            is_active = (active_group == i)
            color = (241, 196, 15) if is_active else (55, 58, 68)
            algo_name = algos[i][group_idx[i]]
            btn_rect = ui_rects[f'grp{i}']
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=6)
            # Bright border: white when active, gray when inactive
            border_col = (255, 255, 255) if is_active else (130, 135, 150)
            pygame.draw.rect(self.screen, border_col, btn_rect, width=2, border_radius=6)
            txt_col = (20, 20, 20) if is_active else (230, 232, 240)
            lbl = self.bold_font.render(f"N{i}: {algo_name}", True, txt_col)
            self.screen.blit(lbl, (btn_rect.centerx - lbl.get_width() / 2, btn_rect.centery - lbl.get_height() / 2))

        # BẢNG SO SÁNH HIỆU NĂNG REAL-TIME
        # Title with accent underline
        title_surf = self.title_font.render("SO SÁNH HIỆU NĂNG", True, (255, 215, 0))
        self.screen.blit(title_surf, (MAP_WIDTH + 15, 385))
        pygame.draw.line(self.screen, (255, 215, 0), (MAP_WIDTH + 15, 385 + title_surf.get_height() + 2),
                         (MAP_WIDTH + 15 + title_surf.get_width(), 385 + title_surf.get_height() + 2), 2)
        
        # Tiêu đề cột - bright white
        self.screen.blit(self.bold_font.render("Thuật toán", True, (255, 255, 255)), (MAP_WIDTH + 12, 422))
        self.screen.blit(self.bold_font.render("Khách", True, (255, 255, 255)), (MAP_WIDTH + 120, 422))
        self.screen.blit(self.bold_font.render("Chi phí", True, (255, 255, 255)), (MAP_WIDTH + 185, 422))
        self.screen.blit(self.bold_font.render("DT", True, (255, 255, 255)), (MAP_WIDTH + 260, 422))
        
        # Đường gạch chân tiêu đề sáng hơn
        pygame.draw.line(self.screen, (140, 145, 165), (MAP_WIDTH + 12, 445), (MAP_WIDTH + DASHBOARD_WIDTH - 12, 445), 1)

        leaderboard = metrics.get('taxi_leaderboard', {})
        y_row = 450
        
        for name, data in leaderboard.items():
            # Zebra stripe for rows
            if list(leaderboard.keys()).index(name) % 2 == 0:
                stripe = pygame.Surface((DASHBOARD_WIDTH - 10, 22), pygame.SRCALPHA)
                stripe.fill((255, 255, 255, 12))
                self.screen.blit(stripe, (MAP_WIDTH + 5, y_row - 2))
            
            self.screen.blit(self.bold_font.render(name, True, (240, 242, 255)), (MAP_WIDTH + 12, y_row))
            self.screen.blit(self.bold_font.render(data.get('customers', '-'), True, (255, 220, 50)), (MAP_WIDTH + 120, y_row))
            self.screen.blit(self.bold_font.render(f"{data['cost']:,}đ", True, (255, 100, 80)), (MAP_WIDTH + 185, y_row))
            self.screen.blit(self.bold_font.render(f"{data['revenue']:,}đ", True, (80, 230, 130)), (MAP_WIDTH + 260, y_row))
            
            y_row += 26

    def _draw_btn(self, rect, text, color, use_small=False):
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        # Bright border always white
        pygame.draw.rect(self.screen, (200, 205, 215), rect, width=2, border_radius=6)
        fnt = self.font if use_small else self.bold_font
        # Determine text color: dark on bright buttons, white on dark buttons
        luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        txt_col = (15, 15, 15) if luminance > 160 else (245, 247, 255)
        txt = fnt.render(text, True, txt_col)
        self.screen.blit(txt, (rect.centerx - txt.get_width() / 2, rect.centery - txt.get_height() / 2))

    def draw_focused_vehicle_ui(self, vehicle):
        pass