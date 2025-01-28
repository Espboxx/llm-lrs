from typing import List, Dict  # 新增类型导入
from modules.validators import ThiefActionValidator
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class DayAction:
    """白天行动基类"""
    actor: str               # 执行者ID
    action_type: str         # 行动类型
    targets: Tuple[str, ...] # 目标玩家列表
    priority: int = 0        # 执行优先级
    extra_data: dict = None  # 附加数据

def process_day_actions(actions: List[DayAction], game_state: Dict):
    role_changes = game_state.setdefault('role_changes', {})
    
    thief_actions = [a for a in actions if a.action_type == "steal_role"]
    for action in thief_actions:
        if ThiefActionValidator.validate(action, game_state):
            # 执行角色替换
            thief = game_state['players'][action.actor].role
            thief.stolen_role = action.extra_data['selected_role']
            role_changes[action.actor] = {
                'old_role': type(thief).__name__,
                'new_role': thief.stolen_role
            }
            # 从剩余角色中移除
            if thief.stolen_role in game_state['remaining_roles']:
                game_state['remaining_roles'].remove(thief.stolen_role) 