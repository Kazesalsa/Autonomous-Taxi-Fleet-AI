from algorithms.registry import ALGORITHM_REGISTRY, GROUP_MAPPING
from core.metrics import ExperimentResult
from typing import Dict, List, Any

class ExperimentRunner:
    def __init__(self):
        self.registry = ALGORITHM_REGISTRY
        self.groups = GROUP_MAPPING

    def run_single(self, algo_name: str, context: Any) -> ExperimentResult:
        if algo_name not in self.registry:
            raise ValueError(f"Algorithm {algo_name} not found in registry.")
        return self.registry[algo_name](context)

    def run_group(self, group_name: str, context: Any) -> List[ExperimentResult]:
        if group_name not in self.groups:
            raise ValueError(f"Group {group_name} not found.")
        
        results = []
        for algo_name in self.groups[group_name]:
            results.append(self.run_single(algo_name, context))
        return results

    def run_all(self, context_map: Dict[str, Any]) -> List[ExperimentResult]:
        results = []
        for group_name, algos in self.groups.items():
            context = context_map.get(group_name)
            if context:
                for algo_name in algos:
                    results.append(self.run_single(algo_name, context))
        return results
