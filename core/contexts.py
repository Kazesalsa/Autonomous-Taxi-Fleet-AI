from dataclasses import dataclass
from typing import Callable, Any, Optional, Dict, List, Set, Tuple

@dataclass
class PathfindingContext:
    graph: Any
    start_id: str
    goal_id: str
    heuristic_fn: Optional[Callable[[Any, Any], float]] = None
    weight: float = 1.0

@dataclass
class TrafficOptimizationContext:
    graph: Any
    light_nodes: List[str]
    objective_fn: Callable[[Dict[str, int]], float]
    initial_state: Dict[str, int]
    max_iterations: int = 1000
    k_beam: int = 3

@dataclass
class CSPContext:
    variables: List[str]
    domains: Dict[str, List[int]]
    constraints: Callable[[str, int, str, int], bool]
    neighbors: Dict[str, List[str]]
    max_steps: int = 1000

@dataclass
class ComplexEnvContext:
    graph: Any
    start_id: str
    goal_id: str
    broken_edges: Dict[Tuple[str, str], Dict[str, Any]]
    heuristic_fn: Callable[[Any, Any], float]
    sensor_range: float = 150.0
