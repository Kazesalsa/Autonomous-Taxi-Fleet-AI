import pygame
import math
from config import MAP_WIDTH, DASHBOARD_WIDTH

class Dashboard:
    def __init__(self):
        self.log_messages = []
        self.metrics = {"distance": 0, "revenue": 0, "status_msg": "", "status_color": (255, 255, 255)}
        self.active_map = 1
        self.active_group = None
        self.group_idx = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.last_click_time = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.algos = {
            1: ["BFS", "DFS", "UCS"],
            2: ["A*", "GBFS", "W-A*"],
            3: ["Hill Climb", "Sim. Anneal", "Genetic"],
            4: ["D* Lite", "RTAA*", "Online"],
            5: ["Backtrack", "AC-3", "Fwd Chk"],
            6: ["Minimax", "Alpha-Beta", "Expect"]
        }
        
        cw = (DASHBOARD_WIDTH - 50) // 2
        c1 = MAP_WIDTH + 20
        c2 = MAP_WIDTH + 30 + cw

        self.ui_rects = {
            'pause': pygame.Rect(MAP_WIDTH + 20, 550, DASHBOARD_WIDTH - 40, 40),
            
            # Hàng 1: Bắt đầu & Dừng (Y = 20)
            'start': pygame.Rect(c1, 20, cw, 35),
            'stop': pygame.Rect(c2, 20, cw, 35),
            
            # Hàng 2: Reset & Vật cản (Y = 65)
            'reset': pygame.Rect(c1, 65, cw, 35),
            'obstacle': pygame.Rect(c2, 65, cw, 35),
            
            # Hàng 3: Kịch bản MAP (Xếp dọc tránh đè chữ)
            'map1': pygame.Rect(MAP_WIDTH + 20, 115, DASHBOARD_WIDTH - 40, 35),
            'map2': pygame.Rect(MAP_WIDTH + 20, 155, DASHBOARD_WIDTH - 40, 35),
            'map3': pygame.Rect(MAP_WIDTH + 20, 195, DASHBOARD_WIDTH - 40, 35),
            
            # Hàng 4: Các nhóm thuật toán (Chiều cao thu nhỏ về 32px để tiết kiệm không gian)
            'grp1': pygame.Rect(c1, 245, cw, 32),
            'grp2': pygame.Rect(c2, 245, cw, 32),
            'grp3': pygame.Rect(c1, 285, cw, 32),
            'grp4': pygame.Rect(c2, 285, cw, 32),
            'grp5': pygame.Rect(c1, 325, cw, 32),
            'grp6': pygame.Rect(c2, 325, cw, 32),
            '_state_sync': {}
        }
        self._sync_state()

    def add_log(self, message):
        self.log_messages.append(message)
        if len(self.log_messages) > 15: self.log_messages.pop(0)

    def reset_scenario_data(self):
        self.metrics = {"distance": 0, "revenue": 0, "status_msg": "", "status_color": (255, 255, 255)}
        self._sync_state()

    def _sync_state(self):
        # Đảm bảo giữ cấu trúc taxi_leaderboard động để cập nhật điểm từ xe thực tế
        leaderboard = self.metrics.get('taxi_leaderboard', {})
        self.ui_rects['_state_sync'] = {
            'active_map': self.active_map,
            'active_group': self.active_group,
            'group_idx': self.group_idx,
            'algos': self.algos,
            'metrics': self.metrics,
            'obstacle_mode': False
        }

    def handle_click(self, pos, graph, vehicles, broken_edges, button=1):
        if pos[0] >= MAP_WIDTH:
            is_right_click = (button == 3)
            clicked_ui = False
            current_time = pygame.time.get_ticks()
            
            if self.ui_rects['pause'].collidepoint(pos):
                return 'pause'
            if self.ui_rects['start'].collidepoint(pos):
                return 'pause'
            if self.ui_rects['stop'].collidepoint(pos):
                return 'stop'
            if self.ui_rects['reset'].collidepoint(pos):
                return 'reset'
            if self.ui_rects['obstacle'].collidepoint(pos):
                return 'obstacle'

            for i in range(1, 4):
                if self.ui_rects[f'map{i}'].collidepoint(pos):
                    self.active_map = i
                    self.reset_scenario_data()
                    return ("START_SCENARIO", i)

            for i in range(1, 7):
                if self.ui_rects[f'grp{i}'].collidepoint(pos):
                    if current_time - self.last_click_time[i] < 500 and button == 1:
                        self.last_click_time[i] = current_time
                        return ("SPAWN_TAXI", i, self.algos[i][self.group_idx[i]])
                    
                    self.last_click_time[i] = current_time
                    
                    if is_right_click:
                        self.group_idx[i] = (self.group_idx[i] + 1) % len(self.algos[i])
                        self.active_group = i
                    else:
                        self.active_group = i if self.active_group != i else None
                    clicked_ui = True

            if clicked_ui:
                # ĐÃ LOẠI BỎ TOÀN BỘ LOGIC TỰ TĂNG KHOẢNG CÁCH/TIỀN GIẢ LẬP ĐỂ KHÔNG BỊ SAI SỐ
                self._sync_state()
                return "UI_UPDATED"

            return None

        for edge_id, obs in list(broken_edges.items()):
            if math.hypot(pos[0] - obs['pos'][0], pos[1] - obs['pos'][1]) < 25:
                return ("REMOVE_BLOCK", edge_id)

        clicked_node = None
        for n_id, n in graph.nodes.items():
            if math.hypot(pos[0] - n.x, pos[1] - n.y) < 25:
                clicked_node = n_id
                break
        if clicked_node: return ("NODE", clicked_node)

        for v in vehicles:
            if math.hypot(pos[0] - v.x, pos[1] - v.y) < 25:
                return ("FOCUS", v)

        min_dist, closest_edge, proj, edge_dir = 30, None, None, None
        for u_id, u_node in graph.nodes.items():
            for edge in u_node.edges:
                v_node = graph.nodes[edge.target_id]
                dist, p = self._dist_point_to_segment(pos, (u_node.x, u_node.y), (v_node.x, v_node.y))
                if dist < min_dist:
                    dx, dy = v_node.x - u_node.x, v_node.y - u_node.y
                    mag = max(0.001, math.hypot(dx, dy))
                    min_dist, closest_edge, proj, edge_dir = dist, (u_id, v_node.node_id), p, (dx/mag, dy/mag)
        if closest_edge: return ("EDGE", closest_edge[0], closest_edge[1], proj, edge_dir)
        return None

    def _dist_point_to_segment(self, pos, p1, p2):
        px, py = pos
        x1, y1 = p1
        x2, y2 = p2
        line_mag = math.hypot(x2 - x1, y2 - y1)
        if line_mag == 0: return math.hypot(px - x1, py - y1), (x1, y1)
        u = max(0, min(1, ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / (line_mag ** 2)))
        proj_x, proj_y = x1 + u * (x2 - x1), y1 + u * (y2 - y1)
        return math.hypot(px - proj_x, py - proj_y), (proj_x, proj_y)