class Vehicle:
    def __init__(self):
        self.current_node_id = 'N1'
        self.assigned_customers = []
        self.revenue_earned = 0
        self.has_picked_up = False
        self.target_node_id = None
        self.path = []

customers = [{'start': 'N1', 'goal': 'N2', 'picked_up': False, 'is_manual': True}]

v = Vehicle()
unassigned = [c for c in customers]
v.assigned_customers.append(unassigned.pop(0))

print("Before:", customers)

# Loop frame 1: at start
assigned = v.assigned_customers[0]
if v.current_node_id == assigned['start'] and not assigned.get('picked_up'):
    assigned['picked_up'] = True
    v.has_picked_up = True
    print("Picked up!")

# Simulate moving to goal
v.current_node_id = 'N2'

# Loop frame 2: at goal
if v.current_node_id == assigned['goal'] and assigned.get('picked_up'):
    v.revenue_earned += assigned.get('fare', 10000)
    assigned['delivered'] = True
    v.assigned_customers.pop(0)
    print("Dropped off! Revenue:", v.revenue_earned)

print("After:", customers)
