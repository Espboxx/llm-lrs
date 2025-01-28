from typing import List, Dict
from .base_actions import BaseNightAction
from modules.validators import (
    SeerActionValidator,
    WitchActionValidator,
    GuardActionValidator
)
from dataclasses import dataclass
from typing import Optional

class NightAction(BaseNightAction):
    """具体夜间行动实现"""
    pass

def process_night_actions(actions: List[NightAction], game_state: Dict):
    """处理夜间行动（按优先级排序）"""
    # 按优先级排序（数值小的先执行）
    sorted_actions = sorted(actions, key=lambda x: x.priority)
    
    # 执行预言家查验
    check_actions = [a for a in sorted_actions if a.action_type == "check_identity"]
    for action in check_actions:
        if SeerActionValidator.validate(action, game_state):
            target_role = game_state['players'][action.target].role
            # 将结果传递给预言家
            game_state['players'][action.actor].role.receive_check_result({
                'target': action.target,
                'role': type(target_role).__name__,
                'team': target_role.team.value
            })
    
    # 先处理女巫的解药
    heal_actions = [a for a in sorted_actions if a.action_type == "heal"]
    for action in heal_actions:
        if WitchActionValidator.validate(action, game_state):
            game_state['night_deaths'].discard(action.target)  # 移除死亡
            
    # 处理女巫的毒药
    poison_actions = [a for a in sorted_actions if a.action_type == "poison"]
    for action in poison_actions:
        if WitchActionValidator.validate(action, game_state):
            game_state['night_deaths'].add(action.target)
    
    # 先处理守卫的守护
    protect_actions = [a for a in sorted_actions if a.action_type == "protect"]
    protected_players = set()
    for action in protect_actions:
        if GuardActionValidator.validate(action, game_state):
            protected_players.add(action.target)
    
    # 处理狼人杀人（考虑守护）
    werewolf_actions = [a for a in sorted_actions if a.action_type == "kill"]
    for action in werewolf_actions:
        if action.target not in protected_players:
            game_state['night_deaths'].add(action.target)
    
    # 其他行动处理保持不变... 