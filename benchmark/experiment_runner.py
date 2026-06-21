from algorithms.registry import ALGORITHM_REGISTRY, GROUP_MAPPING
from core.metrics import ExperimentResult
from typing import Dict, List, Any

class ExperimentRunner:
    def __init__(self):
        self.registry = ALGORITHM_REGISTRY
        self.groups = GROUP_MAPPING
    def run_single(self, algo_name: str, context: Any) -> ExperimentResult:
        if algo_name not in self.registry: raise ValueError(f"Algorithm {algo_name} not found.")
        return self.registry[algo_name](context)
    def run_group(self, group_name: str, context: Any) -> List[ExperimentResult]:
        if group_name not in self.groups: raise ValueError(f"Group {group_name} not found.")
        return [self.run_single(algo, context) for algo in self.groups[group_name]]
    def run_all(self, context_map: Dict[str, Any]) -> List[ExperimentResult]:
        return [self.run_single(algo, context_map[grp]) for grp, algos in self.groups.items() if grp in context_map for algo in algos]
