import time
import heapq
from collections import deque
from core.metrics import ExperimentResult

def run_and_or_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    nodes_expanded = [0]
    def or_search(state, path):
        nodes_expanded[0] += 1
        if state == context.goal_id: return []
        if state in path: return None
        for edge in context.graph.nodes[state].edges:
            action = edge.target_id
            e_tuple = tuple(sorted((state, action)))
            if e_tuple in context.broken_edges and context.broken_edges[e_tuple]['type'] != 'CROSSWALK':
                plan = and_search(state, action, path + [state])
                if plan is not None: return {action: plan}
            else:
                plan = or_search(action, path + [state])
                if plan is not None: return {action: plan}
        return None
    def and_search(state, action, path):
        nodes_expanded[0] += 1
        p_clear = or_search(action, path)
        if p_clear is None: return None
        p_blocked = or_search(state, path)
        if p_blocked is None: return None
        return {"if_clear": p_clear, "if_blocked": p_blocked}
    result = or_search(context.start_id, [])
    
    # Flatten decision tree to a single path
    path = []
    curr_tree = result
    curr_node = context.start_id
    while isinstance(curr_tree, dict):
        if "if_clear" in curr_tree:
            curr_tree = curr_tree["if_clear"]
        else:
            action = list(curr_tree.keys())[0]
            path.append(action)
            curr_tree = curr_tree[action]
            
    if path: path = [context.start_id] + path
    return ExperimentResult("AND-OR Search", "Complex Env", result is not None, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded[0]}, path)

def run_online_replanning(context) -> ExperimentResult:
    start_time = time.perf_counter()
    def a_star(graph, start_id, goal_id, h_fn, known_broken):
        open_set = []
        heapq.heappush(open_set, (0, start_id))
        came_from, g_score = {start_id: None}, {start_id: 0}
        while open_set:
            _, curr = heapq.heappop(open_set)
            if curr == goal_id:
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = came_from[curr]
                return path[::-1]
            for edge in graph.nodes[curr].edges:
                nxt = edge.target_id
                if tuple(sorted((curr, nxt))) in known_broken: continue
                tentative_g = g_score[curr] + edge.get_weight()
                if tentative_g < g_score.get(nxt, float('inf')):
                    came_from[nxt], g_score[nxt] = curr, tentative_g
                    heapq.heappush(open_set, (tentative_g + h_fn(graph.nodes[nxt], graph.nodes[goal_id]), nxt))
        return []
    curr, goal, known = context.start_id, context.goal_id, set()
    actual_path, replans, nodes_expanded = [curr], 0, 0
    while curr != goal:
        plan = a_star(context.graph, curr, goal, context.heuristic_fn, known)
        if not plan: break
        nxt = plan[1]
        nodes_expanded += len(plan)
        if tuple(sorted((curr, nxt))) in context.broken_edges and context.broken_edges[tuple(sorted((curr, nxt)))]['type'] != 'CROSSWALK':
            known.add(tuple(sorted((curr, nxt))))
            replans += 1
        else:
            curr = nxt
            actual_path.append(curr)
    return ExperimentResult("Online Replanning", "Complex Env", curr == goal, (time.perf_counter() - start_time) * 1000, {"replans": replans, "nodes_expanded": nodes_expanded}, actual_path)

def run_sensorless_search(context) -> ExperimentResult:
    start_time = time.perf_counter()
    initial_belief = frozenset([context.start_id])
    queue = deque([(initial_belief, [context.start_id])])
    visited = {initial_belief}
    nodes_expanded, success, final_path = 0, False, []
    while queue:
        belief, path = queue.popleft()
        nodes_expanded += 1
        if belief == frozenset([context.goal_id]):
            success, final_path = True, path
            break
        possible_actions = set()
        for state in belief:
            for edge in context.graph.nodes[state].edges:
                possible_actions.add(edge.target_id)
        for action in possible_actions:
            next_belief = set()
            for state in belief:
                can_move = False
                for edge in context.graph.nodes[state].edges:
                    if edge.target_id == action:
                        next_belief.add(action)
                        can_move = True
                        break
                if not can_move: next_belief.add(state)
            nbf = frozenset(next_belief)
            if nbf not in visited:
                visited.add(nbf)
                queue.append((nbf, path + [action]))
    return ExperimentResult("Sensorless Search", "Complex Env", success, (time.perf_counter() - start_time) * 1000, {"nodes_expanded": nodes_expanded}, final_path)
