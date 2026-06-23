import random

EDGE_NODES = ['N10', 'N24', 'N31', 'N27', 'N13', 'N20', 'N45', 'N57', 'N82', 'N81', 'N80', 'N79', 'N38', 'N37', 'N35', 'N6', 'N1', 'N17']

def spawn_scenario_customers(map_id, graph):
    customers = []
    if map_id == 1:
        start = random.choice(list(graph.nodes.keys()))
        goal = random.choice(list(graph.nodes.keys()))
        customers.append({'id': 1, 'start': start, 'goal': goal, 'status': 'WAITING', 'agree_to_share': True})
    elif map_id == 2:
        customers = [
            {'id': 'A', 'start': 'N1', 'goal': 'N12', 'status': 'WAITING', 'agree_to_share': True},
            {'id': 'B', 'start': 'N2', 'goal': 'N13', 'status': 'WAITING', 'agree_to_share': True},
            {'id': 'C_VIP', 'start': 'N3', 'goal': 'N16', 'status': 'WAITING', 'agree_to_share': False},
            {'id': 'D', 'start': 'N5', 'goal': 'N41', 'status': 'WAITING', 'agree_to_share': True}
        ]
    return customers

def spawn_taxi(group_id, algo_name, graph, vehicles_list, VehicleClass):
    start_node = random.choice(EDGE_NODES)
    v_id = f"TX_{len(vehicles_list) + 1}_{algo_name.replace(' ', '')}"
    
    new_taxi = VehicleClass(v_id, start_node)
    new_taxi.algo_group = group_id
    new_taxi.algo_name = algo_name
    
    node_obj = graph.nodes[start_node]
    new_taxi.x = node_obj.x
    new_taxi.y = node_obj.y
    new_taxi.current_node_id = start_node
    new_taxi.current_edge_start_id = start_node
    new_taxi.target_node_id = None
    new_taxi.angle = 0.0
    new_taxi.state = "MOVING"
    
    vehicles_list.append(new_taxi)
    return new_taxi