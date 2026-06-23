import random

# Đồng bộ mảng EDGE_NODES chuẩn chữ Hoa đồng nhất với hệ thống bản đồ mới
EDGE_NODES = ['N1', 'N17', 'N6', 'N35', 'N79', 'N80', 'N82', 'N81', 'N45', 'N57', 'N20', 'N13', 'N27', 'N31', 'N10', 'N24']

def spawn_scenario_customers(map_id, graph):
    """
    Sinh danh sách khách hàng dựa trên kịch bản MAP được chọn.
    Mỗi khách hàng là một dictionary có cấu trúc:
    {
        'id': str,
        'start': str (node_id),
        'goal': str (node_id),
        'agree_to_share': bool (tùy chọn)
    }
    """
    customers_list = []
    all_nodes = list(graph.nodes.keys())
    if not all_nodes:
        return customers_list

    # Kịch bản 1: Tạo 5 khách hàng phân bố ngẫu nhiên hoàn toàn
    if map_id == 1:
        for i in range(5):
            start = random.choice(all_nodes)
            goal = random.choice(all_nodes)
            while goal == start:
                goal = random.choice(all_nodes)
            customers_list.append({
                'id': f"CUST_M1_{i+1}",
                'start': start,
                'goal': goal
            })

    # Kịch bản 2: Tạo 4 khách hàng ngẫu nhiên có thêm thuộc tính đồng ý / không ghép khách
    elif map_id == 2:
        for i in range(4):
            start = random.choice(all_nodes)
            goal = random.choice(all_nodes)
            while goal == start:
                goal = random.choice(all_nodes)
            customers_list.append({
                'id': f"CUST_M2_{i+1}",
                'start': start,
                'goal': goal,
                'agree_to_share': random.choice([True, False]) # Đồng ý hoặc từ chối đi chung xe
            })

    # Kịch bản 3: Khởi tạo 4 khách hàng ngẫu nhiên ban đầu
    elif map_id == 3:
        for i in range(4):
            start = random.choice(all_nodes)
            goal = random.choice(all_nodes)
            while goal == start:
                goal = random.choice(all_nodes)
            customers_list.append({
                'id': f"CUST_M3_{i+1}",
                'start': start,
                'goal': goal
            })

    return customers_list


def spawn_taxi(group_id, algo_name, graph, vehicles_list, vehicle_class):
    """
    Sinh xe taxi xuất phát ngẫu nhiên từ danh sách các nút rìa cố định hệ thống
    """
    start_node = random.choice(EDGE_NODES)
    v_id = f"TX_{len(vehicles_list) + 1}_{algo_name.replace(' ', '')}"
    
    v = vehicle_class(v_id, start_node)
    v.state = "MOVING"
    vehicles_list.append(v)
    return v