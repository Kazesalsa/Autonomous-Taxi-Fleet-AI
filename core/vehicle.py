import random
import math
from config import VEHICLE_SPEED_BASE, ROAD_WIDTH

class Vehicle:
    def __init__(self, v_id, start_node_id, is_ambulance=False):
        self.v_id = v_id
        self.current_node_id = start_node_id
        self.path = []
        self.is_ambulance = is_ambulance
        self.lane = 0
        self.x = 0
        self.y = 0
        self.target_node_id = None
        self.current_edge_start_id = start_node_id
        self.final_goal_id = None
        self.angle = 0
        
        self.pull_over_offset = 0.0
        self.u_turn_progress = 0.0
        self.start_uturn_angle = 0.0
        self.new_path_pending = None
        self.stuck_target = None
        
        self.status = "AMBULANCE" if is_ambulance else "IDLE"
        self.customer_goal = None
        self.state = "IDLE_IN_DEPOT"
        
        if v_id.startswith('TX_'):
            self.distance_traveled = 0
            self.revenue_earned = 0
            self.has_picked_up = False

    def set_path(self, path, graph):
        if not path: return
        self.final_goal_id = path[-1]
        self.path = list(path)
        if len(self.path) > 1:
            new_current = self.path.pop(0)
            new_target = self.path[0]
            
            same_start_node = (self.current_edge_start_id == new_current)
            
            self.current_node_id = new_current
            self.current_edge_start_id = self.current_node_id
            self.target_node_id = new_target
            
            if self.current_node_id in graph.nodes and self.target_node_id in graph.nodes:
                n1 = graph.nodes[self.current_node_id]
                n2 = graph.nodes[self.target_node_id]
                
                if (self.x == 0 and self.y == 0) or not same_start_node:
                    self.x = n1.x
                    self.y = n1.y
                
                self.angle = math.atan2(n2.y - self.y, n2.x - self.x)

    def update_position(self, graph):
        if self.state in ["STUCK_AT_OBSTACLE", "IDLE_IN_DEPOT"]: 
            return False

        if self.state == "U_TURNING":
            speed = VEHICLE_SPEED_BASE * 1.5
            self.u_turn_progress += speed / 18.0
            if self.u_turn_progress >= math.pi:
                self.angle = self.start_uturn_angle + math.pi
                self.state = "MOVING"
                self.u_turn_progress = 0.0
                temp = self.target_node_id
                self.target_node_id = self.current_edge_start_id
                self.current_edge_start_id = temp
                if self.new_path_pending:
                    self.path = self.new_path_pending[1:]
                    self.new_path_pending = None
            else:
                self.angle += speed / 18.0
            return False

        if self.state in ["SAFE_WAIT", "WAIT_U_TURN"]: 
            return False

        if not self.target_node_id or self.current_node_id not in graph.nodes or self.target_node_id not in graph.nodes:
            return True

        target_node = graph.nodes[self.target_node_id]
        start_node = graph.nodes[self.current_edge_start_id]
        
        speed = (VEHICLE_SPEED_BASE * 1.4 * 0.6) if self.is_ambulance else (VEHICLE_SPEED_BASE * 0.75)

        dx_road = target_node.x - start_node.x
        dy_road = target_node.y - start_node.y
        dx = target_node.x - self.x
        dy = target_node.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0: self.angle = math.atan2(dy, dx)

        # --- FIX BUG: GIẢM KHOẢNG CÁCH DỪNG XUỐNG 28 ĐỂ SÁT VẠCH NGÃ TƯ ---
        # Changed to 73 to match the previous 2nd car's stopping position (28 + 45)
        stop_dist = 73
        
        is_red_light = False
        if getattr(target_node, 'has_light', False) and not self.is_ambulance:
            axis = 'H' if abs(dx_road) > abs(dy_road) else 'V'
            my_light_state = 'RED'
            
            if target_node.light_state == 'H_GREEN' and axis == 'H': my_light_state = 'GREEN'
            elif target_node.light_state == 'H_YELLOW' and axis == 'H': my_light_state = 'YELLOW'
            elif target_node.light_state == 'V_GREEN' and axis == 'V': my_light_state = 'GREEN'
            elif target_node.light_state == 'V_YELLOW' and axis == 'V': my_light_state = 'YELLOW'
            
            if my_light_state in ['RED', 'YELLOW']:
                is_red_light = True
                
        # Bỏ qua đèn đỏ nếu đoạn đường quá ngắn (các đoạn nối bên trong nội bộ ngã tư)
        dist_road = math.hypot(dx_road, dy_road)
        if dist_road <= 60:
            is_red_light = False
                
        # Dừng chính xác tại vạch nếu đèn đỏ, nếu đã vượt vạch (vào giữa ngã tư) thì đi tiếp
        if is_red_light and dist > stop_dist - 0.1:
            if dist - speed <= stop_dist:
                actual_step = dist - stop_dist
                if actual_step > 0:
                    self.x += (dx / dist) * actual_step
                    self.y += (dy / dist) * actual_step
                return False 

        actual_step = 0
        if dist <= speed:
            actual_step = dist
            self.x = target_node.x
            self.y = target_node.y
            self.current_node_id = self.target_node_id
            self.current_edge_start_id = self.current_node_id
            if getattr(target_node, 'csp_locked', False) and self.is_ambulance: target_node.csp_locked = False
            if self.path: 
                self.target_node_id = self.path.pop(0)
                next_node = graph.nodes[self.target_node_id]
                self.angle = math.atan2(next_node.y - self.y, next_node.x - self.x)
            else: self.target_node_id = None
        else:
            actual_step = speed
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            
        # Tích lũy quãng đường và phân chia chi phí/doanh thu thực tế theo hành trình đón khách
        if self.v_id.startswith('TX_'):
            if not hasattr(self, 'distance_traveled'): self.distance_traveled = 0
            if not hasattr(self, 'revenue_earned'): self.revenue_earned = 0
            if not hasattr(self, 'has_picked_up'): self.has_picked_up = False

            self.distance_traveled += actual_step

            if self.has_picked_up:
                # Giai đoạn chở khách kèm lợi nhuận: 10px = 1500VND -> 1px = 150VND
                self.revenue_earned += actual_step * 150

        return False

class Ambulance(Vehicle):
    def __init__(self, v_id, start_node_id):
        super().__init__(v_id, start_node_id, is_ambulance=True)
        self.state = "IDLE_AT_HOSPITAL"
        self.park_node = start_node_id
        self.patient_node = None
        self.color = (255, 255, 255) # White body

    def dispatch(self, patient_node_id, graph, path_to_patient, customer_dict=None):
        self.patient_node = patient_node_id
        self.state = "MOVING_TO_PATIENT"
        self.customer_dict = customer_dict
        self.set_path(path_to_patient, graph)

    def update_position(self, graph):
        # Call base class update_position
        super().update_position(graph)
        
        # State machine logic
        if self.state == "MOVING_TO_PATIENT" and not self.target_node_id:
            # Reached patient!
            self.state = "RETURNING_TO_HOSPITAL"
            if hasattr(self, 'customer_dict') and self.customer_dict:
                self.customer_dict['picked_up'] = True
            
            # Get path back to hospital park_node
            from algorithms.registry import ALGORITHM_REGISTRY
            path_back = ALGORITHM_REGISTRY["A*"](graph, self.current_node_id, self.park_node)
            if path_back and len(path_back) > 1:
                self.set_path(path_back, graph)
            else:
                # Fallback if pathing fails: teleport back to hospital to prevent vanishing
                self.current_node_id = self.park_node
                self.target_node_id = None
                self.state = "IDLE_AT_HOSPITAL"
                self.patient_node = None
                n = graph.nodes[self.park_node]
                self.x, self.y = n.x, n.y
                if self.park_node in ['N103', 'N108']: self.x += 15
                elif self.park_node in ['N106', 'N107']: self.x -= 12
                
        elif self.state == "RETURNING_TO_HOSPITAL" and not self.target_node_id:
            # Reached hospital park_node!
            self.state = "IDLE_AT_HOSPITAL"
            self.patient_node = None
            if hasattr(self, 'customer_dict') and self.customer_dict:
                self.customer_dict['delivered'] = True
            if self.park_node in ['N103', 'N108']: self.x += 15
            elif self.park_node in ['N106', 'N107']: self.x -= 12
class ManualTaxi(Vehicle):
    def __init__(self, v_id, start_node_id):
        super().__init__(v_id, start_node_id)
        self.state = "IDLE_AT_PARKING"
        self.customer_dict = None
        self.park_node = start_node_id
        self.completed_trips = 0

    def dispatch(self, customer_dict, graph):
        self.customer_dict = customer_dict
        self.state = "MOVING_TO_CUSTOMER"
        self.has_picked_up = False
        
        from algorithms.registry import ALGORITHM_REGISTRY
        p = ALGORITHM_REGISTRY.get(getattr(self, 'algo', 'A*'), ALGORITHM_REGISTRY['A*'])(graph, self.current_node_id, self.customer_dict['start'])
        if p and len(p) > 1: self.set_path(p, graph)

    def update_position(self, graph):
        super().update_position(graph)
        
        if self.state == "MOVING_TO_CUSTOMER" and not self.target_node_id:
            if self.customer_dict and self.current_node_id != self.customer_dict['start']:
                self.state = "STUCK"
                return
            # Đã tới điểm đón khách
            self.state = "MOVING_TO_GOAL"
            self.has_picked_up = True
            if self.customer_dict:
                self.customer_dict['picked_up'] = True
            
            from algorithms.registry import ALGORITHM_REGISTRY
            p = ALGORITHM_REGISTRY.get(getattr(self, 'algo', 'A*'), ALGORITHM_REGISTRY['A*'])(graph, self.current_node_id, self.customer_dict['goal'])
            if p and len(p) > 1: self.set_path(p, graph)
            
        elif self.state == "MOVING_TO_GOAL" and not self.target_node_id:
            if self.customer_dict and self.current_node_id != self.customer_dict['goal']:
                self.state = "STUCK"
                return
            # Đã tới điểm trả khách
            self.state = "RETURNING_TO_PARKING"
            self.has_picked_up = False
            self.completed_trips += 1
            if self.customer_dict:
                self.customer_dict['delivered'] = True
                self.customer_dict = None
                
            TAXI_PARKING_NODES = ['N111', 'N112', 'N114', 'N115', 'N116', 'N117']
            self.park_node = random.choice(TAXI_PARKING_NODES)
            
            from algorithms.registry import ALGORITHM_REGISTRY
            p = ALGORITHM_REGISTRY.get(getattr(self, 'algo', 'A*'), ALGORITHM_REGISTRY['A*'])(graph, self.current_node_id, self.park_node)
            if p and len(p) > 1: self.set_path(p, graph)
            
        elif self.state == "RETURNING_TO_PARKING" and not self.target_node_id:
            if hasattr(self, 'park_node') and self.current_node_id != self.park_node:
                self.state = "STUCK"
                return
            self.state = "IDLE_AT_PARKING"
