import random

EDGE_NODES = ['N1', 'N17', 'N6', 'N35', 'N79', 'N80', 'N82', 'N81', 'N45', 'N57', 'N20', 'N13', 'N27', 'N31', 'N10', 'N24']

def spawn_scenario_customers(map_id, graph):
    customers_list = []
    all_nodes = list(graph.nodes.keys())
    if not all_nodes:
        return customers_list
        
    labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # Kịch bản 1: 2 khách hàng, cùng chung 1 điểm đón và 1 điểm trả
    if map_id == 1:
        start = random.choice(all_nodes)
        goal = random.choice(all_nodes)
        while goal == start:
            goal = random.choice(all_nodes)
        for i in range(2):
            customers_list.append({
                'id': f"CUST_M1_{i+1}",
                'start': start,
                'goal': goal,
                'label': labels[i],
                'agree_to_share': True
            })

    # Kịch bản 2: Tạo khách hàng hỗn hợp (có khách không muốn ghép xe)
    elif map_id == 2:
        for i in range(5):
            start = random.choice(all_nodes)
            goal = random.choice(all_nodes)
            while goal == start:
                goal = random.choice(all_nodes)
            # 2 khách đầu không cho ghép xe, các khách sau cho ghép
            agree = False if i < 2 else True 
            customers_list.append({
                'id': f"CUST_M2_{i+1}",
                'start': start,
                'goal': goal,
                'label': labels[i],
                'agree_to_share': agree
            })

    # Kịch bản 3: 4 khách ngẫu nhiên mặc định
    elif map_id == 3:
        for i in range(4):
            start = random.choice(all_nodes)
            goal = random.choice(all_nodes)
            while goal == start:
                goal = random.choice(all_nodes)
            customers_list.append({
                'id': f"CUST_M3_{i+1}",
                'start': start,
                'goal': goal,
                'label': labels[i],
                'agree_to_share': True
            })

    return customers_list

def spawn_taxi(group_id, algo_name, start_node, graph, vehicles_list, vehicle_class):
    v_id = f"TX_{len(vehicles_list) + 1}_{algo_name.replace(' ', '')}"
    v = vehicle_class(v_id, start_node)
    if not hasattr(v, "state") or v.state not in ["IDLE_AT_PARKING", "IDLE_AT_HOSPITAL"]: v.state = "MOVING"
    v.group_id = group_id
    v.algo = algo_name
    v.assigned_customers = [] # Hỗ trợ mảng khách hàng để ghép xe
    vehicles_list.append(v)
    return v