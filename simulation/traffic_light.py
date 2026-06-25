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

    def apply_csp_override(self, configs):
        self.csp_overrides = configs

    def build_csp_context(self, graph, vehicles):
        from core.contexts import CSPContext
        variables = list(self.intersections.keys())
        domains = {v: ['H_GREEN', 'V_GREEN'] for v in variables}
        neighbors = {
            'TL': ['TR', 'BL'],
            'TR': ['TL'],
            'BL': ['TL', 'BM'],
            'BM': ['BL', 'BR'],
            'BR': ['BM']
        }
        
        for v in vehicles:
            if getattr(v, 'is_ambulance', False) and v.target_node_id:
                for grp, nodes in self.node_mapping.items():
                    if v.target_node_id in nodes:
                        n_target = graph.nodes[v.target_node_id]
                        dx = abs(n_target.x - v.x)
                        dy = abs(n_target.y - v.y)
                        if dx > dy:
                            domains[grp] = ['H_GREEN']
                        else:
                            domains[grp] = ['V_GREEN']
                        break

        def constraints(var, val, n, val_n):
            return val == val_n

        return CSPContext(variables, domains, constraints, neighbors, max_steps=50)

    def optimize_lights(self, graph, vehicles):
        from algorithms.csp import run_min_conflicts
        ctx = self.build_csp_context(graph, vehicles)
        res = run_min_conflicts(ctx)
        if res and res.path:
            self.apply_csp_override(res.path)

    def update(self, graph, vehicles=None):
        if not hasattr(self, 'csp_update_timer'):
            self.csp_update_timer = 0
            
        self.csp_update_timer += 1
        if vehicles and self.csp_update_timer >= 60:
            self.optimize_lights(graph, vehicles)
            self.csp_update_timer = 0

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
            grp_state = self.intersections[sp_data['group']]['state']
            axis = sp_data['axis']
            light_color = (231, 76, 60)
            if axis == 'H':
                if grp_state == 'H_GREEN': light_color = (46, 204, 113)
                elif grp_state == 'H_YELLOW': light_color = (241, 196, 15)
            elif axis == 'V':
                if grp_state == 'V_GREEN': light_color = (46, 204, 113)
                elif grp_state == 'V_YELLOW': light_color = (241, 196, 15)
            colors[sp_id] = {'pos': sp_data['pos'], 'color': light_color, 'axis': axis}
        return colors