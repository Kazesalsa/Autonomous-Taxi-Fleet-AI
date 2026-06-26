import sys
import os
sys.path.append('.')
from core.map_data import EDGES_DATA

mall_nodes = ['N89', 'N90', 'N91', 'N97', 'N101', 'N102', 'N110']
parking_nodes = ['N114', 'N115', 'N116', 'N117']

print("Edges from Mall:")
for u, v in EDGES_DATA:
    if u in mall_nodes and v not in mall_nodes:
        print(f"{u} -> {v}")

print("Edges from Parking:")
for u, v in EDGES_DATA:
    if u in parking_nodes and v not in parking_nodes:
        print(f"{u} -> {v}")

