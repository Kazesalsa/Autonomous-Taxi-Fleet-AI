import random

EDGE_NODES = ['N1', 'N17', 'N6', 'N35', 'N79', 'N80', 'N82', 'N81', 'N45', 'N57', 'N20', 'N13', 'N27', 'N31', 'N10', 'N24']


def spawn_taxi(group_id, algo_name, start_node, graph, vehicles_list, vehicle_class):
    v_id = f"TX_{len(vehicles_list) + 1}_{algo_name.replace(' ', '')}"
    v = vehicle_class(v_id, start_node)
    if not hasattr(v, "state") or v.state not in ["IDLE_AT_PARKING", "IDLE_AT_HOSPITAL"]: v.state = "MOVING"
    v.group_id = group_id
    v.algo = algo_name
    v.assigned_customers = [] 
    vehicles_list.append(v)
    return v