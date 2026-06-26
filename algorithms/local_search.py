import time
import random
import math
from core.metrics import ExperimentResult

def run_hill_climbing(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id, h_fn = context.graph, context.start_id, context.goal_id, context.heuristic_fn
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return ExperimentResult("Hill Climbing", "Local Search", False, 0.0)
    
    current = start_id
    path = [current]
    nodes_expanded = 0
    
    while current != goal_id:
        nodes_expanded += 1
        best_neighbor = None
        best_h = float('inf')
        
        for edge in graph.nodes[current].edges:
            n_id = edge.target_id
            h = h_fn(n_id, goal_id)
            if h < best_h:
                best_h = h
                best_neighbor = n_id
                
        # Bị kẹt ở cực đại cục bộ (Local Optima) - không có hàng xóm nào gần đích hơn
        if best_neighbor is None or best_h >= h_fn(current, goal_id):
            break
            
        current = best_neighbor
        path.append(current)
        
    success = (current == goal_id)
    return ExperimentResult("Hill Climbing", "Local Search", success, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded, "stuck": not success}, path)

def run_simulated_annealing(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id, h_fn = context.graph, context.start_id, context.goal_id, context.heuristic_fn
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return ExperimentResult("Sim. Anneal", "Local Search", False, 0.0)
    
    current = start_id
    path = [current]
    T = 100.0
    cooling_rate = 0.99
    nodes_expanded = 0
    
    while current != goal_id and T > 0.1:
        nodes_expanded += 1
        neighbors = [edge.target_id for edge in graph.nodes[current].edges]
        if not neighbors:
            break
            
        next_node = random.choice(neighbors)
        current_h = h_fn(current, goal_id)
        next_h = h_fn(next_node, goal_id)
        
        # Nếu tốt hơn (gần đích hơn) -> chấp nhận luôn
        # Nếu xấu hơn (xa đích hơn) -> chấp nhận với xác suất phụ thuộc vào T
        if next_h < current_h or random.random() < math.exp((current_h - next_h) / T):
            current = next_node
            # Tránh path quá dài do đi lòng vòng
            if current in path:
                idx = path.index(current)
                path = path[:idx+1]
            else:
                path.append(current)
                
        T *= cooling_rate
        
    success = (current == goal_id)
    return ExperimentResult("Sim. Anneal", "Local Search", success, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded, "stuck": not success}, path)

def run_local_beam_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    graph, start_id, goal_id, h_fn = context.graph, context.start_id, context.goal_id, context.heuristic_fn
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return ExperimentResult("Local Beam", "Local Search", False, 0.0)
        
    k = getattr(context, 'k_beam', 3)
    # Trạng thái là các path đang duyệt
    beam = [[start_id]]
    nodes_expanded = 0
    
    while beam:
        next_beam = []
        for path in beam:
            current = path[-1]
            if current == goal_id:
                return ExperimentResult("Local Beam", "Local Search", True, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded}, path)
                
            nodes_expanded += 1
            for edge in graph.nodes[current].edges:
                n_id = edge.target_id
                if n_id not in path: # Tránh vòng lặp
                    next_beam.append(path + [n_id])
                    
        if not next_beam:
            break
            
        # Sắp xếp tất cả các ứng viên theo heuristic của node cuối và lấy k best
        next_beam.sort(key=lambda p: h_fn(p[-1], goal_id))
        beam = next_beam[:k]
        
    return ExperimentResult("Local Beam", "Local Search", False, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded, "stuck": True}, beam[0] if beam else [start_id])
