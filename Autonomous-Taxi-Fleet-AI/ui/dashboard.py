import pygame
import math
from config import MAP_WIDTH, DASHBOARD_WIDTH

class Dashboard:
    def __init__(self):
        self.log_messages = []
        self.ui_rects = {
            'pause': pygame.Rect(MAP_WIDTH + 20, 80, DASHBOARD_WIDTH - 40, 40),
            'fog': pygame.Rect(MAP_WIDTH + 20, 130, DASHBOARD_WIDTH - 40, 40),
            'customer': pygame.Rect(MAP_WIDTH + 20, 210, DASHBOARD_WIDTH - 40, 45),
            'crosswalk': pygame.Rect(MAP_WIDTH + 20, 320, DASHBOARD_WIDTH - 40, 35),
            'obstacle': pygame.Rect(MAP_WIDTH + 20, 365, DASHBOARD_WIDTH - 40, 35),
            'ambulance': pygame.Rect(MAP_WIDTH + 20, 410, DASHBOARD_WIDTH - 40, 35)
        }

    def add_log(self, message):
        self.log_messages.append(message)
        if len(self.log_messages) > 15: self.log_messages.pop(0)

    def handle_click(self, pos, graph, vehicles, broken_edges):
        if pos[0] >= MAP_WIDTH:
            for key, rect in self.ui_rects.items():
                if rect.collidepoint(pos): return key
            return None

        # Safe Check Remove obstacle
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
