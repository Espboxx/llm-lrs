from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class BaseNightAction:
    """基础夜间行动"""
    actor: str
    action_type: str
    target: Optional[str] = None
    priority: int = 0

@dataclass
class BaseDayAction:
    """基础白天行动"""
    actor: str
    action_type: str
    targets: Tuple[str, ...]
    priority: int = 0
    extra_data: dict = None 