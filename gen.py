import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
graph_path = os.path.join(BASE_DIR, "core", "graph.py")

print("=== ĐANG KHÔI PHỤC VÀ CHUẨN HÓA TOÀN BỘ FILE CORE/GRAPH.PY ===")

graph_clean_content = """import math

class Edge:
    def __init__(self, target_id, distance, traffic_factor=0.0):
        self.target_id = target_id
        self.distance = distance
        self.traffic_factor = traffic_factor

    def get_weight(self):
        if self.traffic_factor == float('inf'): return float('inf')
        return self.distance * (1 + self.traffic_factor)

class Node:
    def __init__(self, node_id, x, y, label=None):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.label = label
        self.edges = []
        self.has_light = False
        self.light_state = 'NONE'
        self.light_duration = 0
        self.yellow_duration = 60
        self.light_timer = 0
        self.csp_locked = False

    def add_edge(self, target_id, distance, traffic_factor=0.0):
        self.edges.append(Edge(target_id, distance, traffic_factor))

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id, x, y, label=None):
        self.nodes[node_id] = Node(node_id, x, y, label)

    def add_bidirectional_edge(self, id1, id2, traffic_factor=0.0):
        if id1 in self.nodes and id2 in self.nodes:
            n1, n2 = self.nodes[id1], self.nodes[id2]
            dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
            n1.add_edge(id2, dist, traffic_factor)
            n2.add_edge(id1, dist, traffic_factor)

    def add_directional_edge(self, from_id, to_id, traffic_factor=0.0):
        if from_id in self.nodes and to_id in self.nodes:
            n1, n2 = self.nodes[from_id], self.nodes[to_id]
            dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
            n1.add_edge(to_id, dist, traffic_factor)

    def get_edge(self, id1, id2):
        if id1 in self.nodes:
            for edge in self.nodes[id1].edges:
                if edge.target_id == id2:
                    return edge
        return None
"""

with open(graph_path, "w", encoding="utf-8") as f:
    f.write(graph_clean_content.strip() + "\\n")

print("[THÀNH CÔNG] Đã làm sạch mã nguồn tệp core/graph.py.")
print("Bây giờ bạn hãy chạy lại hệ thống bằng lệnh: python main.py")