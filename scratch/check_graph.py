import sys
import os
sys.path.append('.')
from core.map_data import NODES_DATA, EDGES_DATA

edges = {}
for u, v in EDGES_DATA:
    if u not in edges:
        edges[u] = []
    edges[u].append(v)

nodes = list(NODES_DATA.keys())

# Find reachable nodes from each node
def bfs(start):
    visited = set([start])
    queue = [start]
    while queue:
        curr = queue.pop(0)
        for neighbor in edges.get(curr, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited

for node in nodes:
    reachable = bfs(node)
    if len(reachable) < len(nodes) // 2:
        print(f"Node {node} can only reach {len(reachable)} nodes: {reachable}")

