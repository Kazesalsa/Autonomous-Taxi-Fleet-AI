import math

class TrafficFlowManager:
    def __init__(self, road_width=40):
        self.road_width = road_width

    def manage_distances(self, vehicles, graph, broken_edges):
        edge_groups = {}
        for v in vehicles:
            if v.state in ["STUCK_AT_OBSTACLE", "IDLE_IN_DEPOT"]: continue
            if v.target_node_id:
                edge = (v.current_edge_start_id, v.target_node_id)
                if edge not in edge_groups: edge_groups[edge] = []
                edge_groups[edge].append(v)

        for edge, cars in edge_groups.items():
            tn = graph.nodes[edge[1]]
            cars.sort(key=lambda c: math.hypot(c.x - tn.x, c.y - tn.y))
            def set_moving(v):
                if v.state != "STUCK_AT_OBSTACLE":
                    if getattr(v, 'is_ambulance', False):
                        picked_up = False
                        if hasattr(v, 'customer_dict') and v.customer_dict:
                            picked_up = v.customer_dict.get('picked_up', False)
                        v.state = "RETURNING_TO_HOSPITAL" if picked_up else "MOVING_TO_PATIENT"
                    elif type(v).__name__ == "ManualTaxi":
                        if getattr(v, 'customer_dict', None):
                            v.state = "MOVING_TO_GOAL" if getattr(v, 'has_picked_up', False) else "MOVING_TO_CUSTOMER"
                        else:
                            v.state = "RETURNING_TO_PARKING"
                    else:
                        v.state = "MOVING"

            if cars: set_moving(cars[0])
            for i in range(1, len(cars)):
                d1 = math.hypot(cars[i-1].x - tn.x, cars[i-1].y - tn.y)
                d2 = math.hypot(cars[i].x - tn.x, cars[i].y - tn.y)
                if (d2 - d1 < 45): cars[i].state = "SAFE_WAIT"
                else: set_moving(cars[i])
