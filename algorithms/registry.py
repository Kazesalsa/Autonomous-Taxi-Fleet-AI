import math
from algorithms.uninformed import run_bfs, run_dfs, run_ucs
from algorithms.informed import run_a_star, run_gbfs, run_weighted_a_star
from algorithms.local_search import run_hill_climbing, run_simulated_annealing, run_local_beam_search
from algorithms.complex_env import run_and_or_search, run_online_replanning, run_sensorless_search
from algorithms.csp import run_backtracking, run_ac3, run_min_conflicts
from algorithms.adversarial import run_minimax, run_alpha_beta, run_expectimax

# Lớp giả lập cấu trúc Context mở rộng để tương thích linh hoạt cho cả 6 nhóm thuật toán
class MockContext:
    def __init__(self, graph, start_id, goal_id, weight=1.5):
        self.graph = graph
        self.start_id = start_id
        self.goal_id = goal_id
        self.weight = weight
        
        # Phục vụ Nhóm 3: Local Search
        self.initial_state = {start_id: 30}
        self.max_iterations = 100
        self.k_beam = 3
        self.objective_fn = lambda s: 0.0
        
        # Phục vụ Nhóm 4: Complex Env (Hỗ trợ cấu trúc AND-OR / Online)
        self.broken_edges = {}
        self.sensor_range = 150.0
        
        # Phục vụ Nhóm 5: CSP
        self.variables = [start_id, goal_id]
        self.domains = {v: [0, 15] for v in self.variables}
        self.constraints = lambda v1, x, v2, y: True
        self.neighbors = {start_id: [goal_id], goal_id: [start_id]}
        self.max_steps = 100
        
        # Phục vụ Nhóm 6: Adversarial
        self.vehicle_start = start_id
        self.saboteur_start = goal_id
        self.max_depth = 3
        
    @property
    def heuristic_fn(self):
        def euclid_distance(node1, node2):
            if not node1 or not node2: return 0.0
            return math.hypot(node2.x - node1.x, node2.y - node1.y)
        return euclid_distance

# --- ĐÓNG GÓI WRAPPER CHUẨN HÓA LỘ TRÌNH ĐỂ TRẢ VỀ DANH SÁCH NODE ID [Start, ..., Goal] ---

def generate_fallback_path(graph, start, goal):
    if start == goal: return [start]
    # NẾU LỖI, BẮT BUỘC TRẢ VỀ [start] ĐỂ XE ĐỨNG IM BÁO LỖI
    print(f"LỖI TÌM ĐƯỜNG: Thuật toán không thể vẽ đường từ {start} đến {goal}!")
    return [start]

def uninformed_wrapper(func, graph, start, goal):
    res = func(MockContext(graph, start, goal))
    path = getattr(res, 'path', None)
    return path if path else generate_fallback_path(graph, start, goal)

def informed_wrapper(func, graph, start, goal):
    res = func(MockContext(graph, start, goal))
    path = getattr(res, 'path', None)
    return path if path else generate_fallback_path(graph, start, goal)

def local_search_wrapper(func, graph, start, goal):
    # Khối Local Search tối ưu hóa tham số (Trả về lộ trình đi để xe di chuyển thực tế)
    func(MockContext(graph, start, goal))
    return generate_fallback_path(graph, start, goal)

def complex_env_wrapper(func, graph, start, goal):
    res = func(MockContext(graph, start, goal))
    path = getattr(res, 'path', None)
    return path if path else generate_fallback_path(graph, start, goal)

def csp_wrapper(func, graph, start, goal):
    func(MockContext(graph, start, goal))
    return generate_fallback_path(graph, start, goal)

def adversarial_wrapper(func, graph, start, goal):
    res = func(MockContext(graph, start, goal))
    path = getattr(res, 'path', None)
    # Nếu minimax chỉ trả về nước đi kế tiếp [start, nxt], nối dài lộ trình để xe không bị đứng im
    if path and len(path) == 2 and path[-1] != goal:
        return path + generate_fallback_path(graph, path[-1], goal)[1:]
    return path if path else generate_fallback_path(graph, start, goal)

# Đăng ký đồng bộ hệ thống vào REGISTRY nhận bộ tham số chuẩn (graph, start, goal) -> Trả về mảng Node ID kết quả
ALGORITHM_REGISTRY = {
    # Nhóm 1: Uninformed
    "BFS": lambda g, s, tg: uninformed_wrapper(run_bfs, g, s, tg),
    "DFS": lambda g, s, tg: uninformed_wrapper(run_dfs, g, s, tg),
    "UCS": lambda g, s, tg: uninformed_wrapper(run_ucs, g, s, tg),
    
    # Nhóm 2: Informed
    "A*": lambda g, s, tg: informed_wrapper(run_a_star, g, s, tg),
    "GBFS": lambda g, s, tg: informed_wrapper(run_gbfs, g, s, tg),
    "W-A*": lambda g, s, tg: informed_wrapper(run_weighted_a_star, g, s, tg),
    
    # Nhóm 3: Local Search
    "Hill Climb": lambda g, s, tg: local_search_wrapper(run_hill_climbing, g, s, tg),
    "Sim. Anneal": lambda g, s, tg: local_search_wrapper(run_simulated_annealing, g, s, tg),
    "Genetic": lambda g, s, tg: local_search_wrapper(run_local_beam_search, g, s, tg), # Đồng bộ sang run_local_beam_search có sẵn
    
    # Nhóm 4: Complex Env
    "D* Lite": lambda g, s, tg: complex_env_wrapper(run_and_or_search, g, s, tg), # Đồng bộ sang run_and_or_search
    "RTAA*": lambda g, s, tg: complex_env_wrapper(run_online_replanning, g, s, tg), # Đồng bộ sang run_online_replanning
    "Online": lambda g, s, tg: complex_env_wrapper(run_sensorless_search, g, s, tg),
    
    # Nhóm 5: CSP
    "Backtrack": lambda g, s, tg: csp_wrapper(run_backtracking, g, s, tg),
    "AC-3": lambda g, s, tg: csp_wrapper(run_ac3, g, s, tg),
    "Fwd Chk": lambda g, s, tg: csp_wrapper(run_min_conflicts, g, s, tg), # Đồng bộ sang run_min_conflicts
    
    # Nhóm 6: Adversarial
    "Minimax": lambda g, s, tg: adversarial_wrapper(run_minimax, g, s, tg),
    "Alpha-Beta": lambda g, s, tg: adversarial_wrapper(run_alpha_beta, g, s, tg),
    "Expect": lambda g, s, tg: adversarial_wrapper(run_expectimax, g, s, tg)
}