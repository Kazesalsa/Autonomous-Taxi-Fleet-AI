import math

class TrafficLightManager:
    def __init__(self):
        self.intersections = {
            'TL': {'state': 'H_GREEN', 'timer': 0, 'duration': 300},
            'TR': {'state': 'V_GREEN', 'timer': 150, 'duration': 300},
            'BL': {'state': 'H_GREEN', 'timer': 80, 'duration': 300},
            'BM': {'state': 'V_GREEN', 'timer': 200, 'duration': 300},
            'BR': {'state': 'H_GREEN', 'timer': 120, 'duration': 300}
        }
        self.node_mapping = {
            'TL': ['N14', 'N7', 'N29', 'N93'],
            'TR': ['N65', 'N12', 'N71', 'N66'],
            'BL': ['N5', 'N22', 'N92'],
            'BM': ['N73', 'N60', 'N74', 'N94'],
            'BR': ['N32', 'N16', 'N33', 'N63']
        }
        
        # FIX: GÁN AXIS CHÉO NHAU (V VÀ H ĐỐI XỨNG QUA TÂM NGÃ TƯ)
        self.sprites = {
            # Ngã tư Dưới - Trái (T-Junction)
            'N109': {'pos': (334, 588), 'group': 'BL', 'axis': 'H'},
            'N110': {'pos': (420, 588), 'group': 'BL', 'axis': 'V'},
            
            # Ngã tư Dưới - Phải
            'N111': {'pos': (859, 586), 'group': 'BR', 'axis': 'V'}, # Trên-Trái
            'N126': {'pos': (942, 662), 'group': 'BR', 'axis': 'V'}, # Dưới-Phải
            'N112': {'pos': (943, 585), 'group': 'BR', 'axis': 'H'}, # Trên-Phải
            'N125': {'pos': (861, 661), 'group': 'BR', 'axis': 'H'}, # Dưới-Trái
            
            # Ngã tư Trên - Phải
            'N113': {'pos': (857, 258), 'group': 'TR', 'axis': 'V'}, # Trên-Trái
            'N115': {'pos': (944, 327), 'group': 'TR', 'axis': 'V'}, # Dưới-Phải
            'N114': {'pos': (943, 256), 'group': 'TR', 'axis': 'H'}, # Trên-Phải
            'N116': {'pos': (858, 327), 'group': 'TR', 'axis': 'H'}, # Dưới-Trái
            
            # Ngã tư Trên - Trái
            'N118': {'pos': (334, 257), 'group': 'TL', 'axis': 'V'}, # Trên-Trái
            'N120': {'pos': (421, 326), 'group': 'TL', 'axis': 'V'}, # Dưới-Phải
            'N117': {'pos': (421, 256), 'group': 'TL', 'axis': 'H'}, # Trên-Phải
            'N119': {'pos': (334, 327), 'group': 'TL', 'axis': 'H'}, # Dưới-Trái
            
            # Ngã tư Dưới - Giữa (Yêu cầu: 116 chéo 119, 117 chéo 118)
            'N121': {'pos': (583, 589), 'group': 'BM', 'axis': 'V'}, # Trên-Trái
            'N124': {'pos': (668, 657), 'group': 'BM', 'axis': 'V'}, # Dưới-Phải
            'N122': {'pos': (667, 590), 'group': 'BM', 'axis': 'H'}, # Trên-Phải
            'N123': {'pos': (583, 657), 'group': 'BM', 'axis': 'H'}  # Dưới-Trái
        }
        self.yellow_time = 60
        self.csp_overrides = {}



    def optimize_lights_ac3(self, graph, vehicles):
        self.csp_overrides.clear()

        ambulances = [v for v in vehicles if getattr(v, 'is_ambulance', False) and getattr(v, 'path', [])]
        required_axes = {}
        target_groups = set()
        
        for ambulance in ambulances:
            # Tăng số node nhìn trước (look ahead) để trưng dụng đèn từ xa và giữ đèn lâu hơn
            route = ambulance.path[:40]
            for node in route:
                for grp_id, nodes in self.node_mapping.items():
                    if node in nodes:
                        target_groups.add(grp_id)
                        if len(route) > 1:
                            dx = abs(graph.nodes[route[-1]].x - graph.nodes[route[0]].x)
                            dy = abs(graph.nodes[route[-1]].y - graph.nodes[route[0]].y)
                            axis_needed = 'H' if dx > dy else 'V'
                            required_axes[grp_id] = axis_needed
                        else:
                            if grp_id not in required_axes:
                                required_axes[grp_id] = 'H' # Default fallback

        if target_groups:
            from algorithms.registry import ASSIGNMENT_REGISTRY
            assignments = ASSIGNMENT_REGISTRY["AC-3"](list(target_groups), required_axes)
            if assignments:
                self.csp_overrides.update(assignments)

    def update(self, graph, vehicles=None):
        if not hasattr(self, 'csp_update_timer'):
            self.csp_update_timer = 0
            
        self.csp_update_timer += 1
        
        # Only count ambulances that are actively moving (have a path)
        has_active_ambulance = any(getattr(v, 'is_ambulance', False) and getattr(v, 'path', []) for v in (vehicles or []))
        
        if has_active_ambulance:
            if self.csp_update_timer >= 10:
                self.optimize_lights_ac3(graph, vehicles)
                self.csp_update_timer = 0
        else:
            self.csp_overrides.clear()

        for key, data in self.intersections.items():
            if key in self.csp_overrides:
                data['state'] = self.csp_overrides[key]
                data['timer'] = 0
            else:
                data['timer'] += 1
                if data['state'] == 'H_GREEN' and data['timer'] >= data['duration']:
                    data['state'] = 'H_YELLOW'; data['timer'] = 0
                elif data['state'] == 'H_YELLOW' and data['timer'] >= self.yellow_time:
                    data['state'] = 'V_GREEN'; data['timer'] = 0
                elif data['state'] == 'V_GREEN' and data['timer'] >= data['duration']:
                    data['state'] = 'V_YELLOW'; data['timer'] = 0
                elif data['state'] == 'V_YELLOW' and data['timer'] >= self.yellow_time:
                    data['state'] = 'H_GREEN'; data['timer'] = 0

            for n_id in self.node_mapping[key]:
                if n_id in graph.nodes:
                    graph.nodes[n_id].has_light = True
                    graph.nodes[n_id].light_state = data['state']

    def get_render_data(self):
        colors = {}
        for sp_id, sp_data in self.sprites.items():
            grp_id = sp_data['group']
            grp_state = self.intersections[grp_id]['state']
            axis = sp_data['axis']
            light_color = (231, 76, 60)
            if axis == 'H':
                if grp_state == 'H_GREEN': light_color = (46, 204, 113)
                elif grp_state == 'H_YELLOW': light_color = (241, 196, 15)
            elif axis == 'V':
                if grp_state == 'V_GREEN': light_color = (46, 204, 113)
                elif grp_state == 'V_YELLOW': light_color = (241, 196, 15)
            colors[sp_id] = {'pos': sp_data['pos'], 'color': light_color, 'axis': axis, 'is_override': grp_id in self.csp_overrides}
        return colors