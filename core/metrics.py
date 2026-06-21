from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class ExperimentResult:
    algorithm_name: str
    group_name: str
    success: bool
    execution_time_ms: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    path: Optional[List[str]] = None
