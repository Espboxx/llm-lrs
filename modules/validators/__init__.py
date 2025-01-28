from typing import Dict, Any, Optional

class ActionValidator:
    """行动验证器基类"""
    @staticmethod
    def validate(action: Any, game_state: Dict) -> bool:
        """验证行动是否合法
        
        Args:
            action: 行动对象
            game_state: 游戏状态
            
        Returns:
            bool: 行动是否合法
        """
        raise NotImplementedError

class SeerActionValidator(ActionValidator):
    """预言家行动验证器"""
    @staticmethod
    def validate(action: Any, game_state: Dict) -> bool:
        # 检查目标是否存活
        if action.target not in game_state['alive_players']:
            return False
        # 检查是否在夜晚阶段
        if game_state['current_phase'] != 'NIGHT':
            return False
        # 检查是否超过最大查验次数
        seer = game_state['players'][action.actor]
        if seer.role.check_count >= game_state['config']['SEER_CONFIG']['max_checks']:
            return False
        return True

class WitchActionValidator(ActionValidator):
    """女巫行动验证器"""
    @staticmethod
    def validate(action: Any, game_state: Dict) -> bool:
        witch = game_state['players'][action.actor]
        # 检查是否有药水可用
        if action.action_type == 'heal' and not witch.role.has_heal_potion:
            return False
        if action.action_type == 'poison' and not witch.role.has_poison_potion:
            return False
        # 检查是否可以自救
        if action.action_type == 'heal' and action.target == action.actor:
            if not game_state['config']['WITCH_CONFIG']['can_save_self']:
                return False
        return True

class GuardActionValidator(ActionValidator):
    """守卫行动验证器"""
    @staticmethod
    def validate(action: Any, game_state: Dict) -> bool:
        guard = game_state['players'][action.actor]
        # 检查是否超过最大守护次数
        if guard.role.protect_count >= game_state['config']['GUARD_CONFIG']['max_protects']:
            return False
        # 检查是否允许连续守护同一玩家
        if not game_state['config']['GUARD_CONFIG']['consecutive_protection']:
            if action.target == guard.role.last_protected:
                return False
        return True

class ThiefActionValidator(ActionValidator):
    """盗贼行动验证器"""
    @staticmethod
    def validate(action: Any, game_state: Dict) -> bool:
        # 检查选择的角色是否在可选列表中
        if action.extra_data['selected_role'] not in game_state['config']['THIEF_CONFIG']['stealable_roles']:
            return False
        return True

class VoteValidator:
    """投票验证器"""
    @staticmethod
    def validate_vote(voter: str, target: Optional[str], game_state: Dict) -> bool:
        """验证投票是否合法
        
        Args:
            voter: 投票者ID
            target: 投票目标ID，None表示弃权
            game_state: 游戏状态
            
        Returns:
            bool: 投票是否合法
        """
        # 检查投票者是否存活
        if voter not in game_state['alive_players']:
            return False
        # 检查投票者是否被沉默
        if game_state['players'][voter].status['silenced']:
            return False
        # 如果不是弃权，检查目标是否存活
        if target is not None and target not in game_state['alive_players']:
            return False
        return True 