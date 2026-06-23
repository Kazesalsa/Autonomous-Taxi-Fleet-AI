import math
import random
from config import VEHICLE_SPEED_BASE, ROAD_WIDTH

class Vehicle:
    def __init__(self, v_id, start_node_id, is_ambulance=False):
        self.v_id = v_id
        self.current_node_id = start_node_id
        self.path = []
        self.is_ambulance = is_ambulance
        self.lane = 0 if is_ambulance else random.choice([0, 1])
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
        
        self.status = "IDLE"
        self.customer_goal = None
        self.state = "IDLE_IN_DEPOT"
        
        if is_ambulance: self.status = "AMBULANCE"

    def set_path(self, path, graph):
        if not path: return
        self.final_goal_id = path[-1]
        self.path = path
        if len(self.path) > 1:
            self.current_node_id = self.path.pop(0)
            self.current_edge_start_id = self.current_node_id
            self.target_node_id = self.path[0]
            if self.current_node_id in graph.nodes and self.target_node_id in graph.nodes:
                n1 = graph.nodes[self.current_node_id]
                self.x = n1.x
                self.y = n1.y

    def update_position(self, graph):
        if self.state in ["STUCK_AT_OBSTACLE", "WAIT_CROSSWALK", "IDLE_IN_DEPOT"]: return False

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

        if self.state in ["YIELD", "SAFE_WAIT", "WAIT_U_TURN"]: return False

        if not self.target_node_id or self.current_node_id not in graph.nodes or self.target_node_id not in graph.nodes:
            return True

        target_node = graph.nodes[self.target_node_id]
        start_node = graph.nodes[self.current_edge_start_id]
        
        speed = VEHICLE_SPEED_BASE * 1.4 if self.is_ambulance else VEHICLE_SPEED_BASE
        if not self.is_ambulance and self.state in ["YIELD_INNER", "YIELD_OUTER"]: speed *= 0.3

        dx_road = target_node.x - start_node.x
        dy_road = target_node.y - start_node.y

        # Điểm đến chính xác là tọa độ của target_node, không cộng thêm bất kỳ độ lệch nào
        dx = target_node.x - self.x
        dy = target_node.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0: 
            target_angle = math.atan2(dy, dx)
            # KHỬ RUNG LẮC: Bù trừ góc quay mềm mại (Low-pass Filter) thay vì bẻ góc gắt
            diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += diff * 0.2

        # --- XỬ LÝ ĐÈN GIAO THÔNG ---
        stop_dist = (ROAD_WIDTH/2 + 10)
        dist_to_center = math.hypot(target_node.x - self.x, target_node.y - self.y)
        if getattr(target_node, 'has_light', False) and target_node.light_state in ['RED', 'YELLOW'] and not self.is_ambulance and dist_to_center < stop_dist:
            axis = 'H' if abs(dx_road) > abs(dy_road) else 'V'
            
            my_light_state = 'RED'
            if target_node.light_state == 'H_GREEN' and axis == 'H': my_light_state = 'GREEN'
            elif target_node.light_state == 'H_YELLOW' and axis == 'H': my_light_state = 'YELLOW'
            elif target_node.light_state == 'V_GREEN' and axis == 'V': my_light_state = 'GREEN'
            elif target_node.light_state == 'V_YELLOW' and axis == 'V': my_light_state = 'YELLOW'
            
            if my_light_state in ['RED', 'YELLOW']:
                return False

        if dist < speed:
            self.current_node_id = self.target_node_id
            self.current_edge_start_id = self.current_node_id
            if getattr(target_node, 'csp_locked', False) and self.is_ambulance: 
                target_node.csp_locked = False

            if self.path: 
                self.target_node_id = self.path.pop(0)
            else: 
                self.target_node_id = None
                self.x = target_node.x
                self.y = target_node.y
        else:
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            
        return False
