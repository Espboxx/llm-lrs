from typing import Dict, Any, Optional
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase
import logging

logger = logging.getLogger(__name__)

class Seer(BaseRole):
    """预言家角色类"""
    
    DEFAULT_RESULT_FORMAT = "你查验的玩家 {target} 的身份是 {role}，属于 {team} 阵营"
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.VILLAGER
        self.check_count = 0  # 查验次数
        self.last_check_result = None  # 上次查验结果
        # 确保使用配置中的查验冷却；若未配置则默认0
        self.cooldowns.setdefault('check', 0)
        # 确保SEER_CONFIG存在
        if 'SEER_CONFIG' not in self.config:
            self.config['SEER_CONFIG'] = {}
        # 设置默认值
        self.config['SEER_CONFIG'].setdefault('result_format', self.DEFAULT_RESULT_FORMAT)
        self.config['SEER_CONFIG'].setdefault('max_checks', 999)
        self.config['SEER_CONFIG'].setdefault('allow_self_check', False)
        self.config['SEER_CONFIG'].setdefault('night_only', True)

    def can_check(self, target_id: str, game_state: Dict[str, Any] = None) -> bool:
        """检查是否可以查验目标
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 是否可以查验
        """
        # 检查基本条件
        if not self.can_use_skill('check'):
            return False
            
        # 检查查验次数限制
        if self.check_count >= self.config['SEER_CONFIG']['max_checks']:
            return False
            
        # 检查是否允许查验自己
        if target_id == self.player_id and not self.config['SEER_CONFIG']['allow_self_check']:
            return False
            
        # 检查是否只能在夜晚查验
        if game_state and self.config['SEER_CONFIG'].get('night_only', True):
            if game_state['current_phase'] != GamePhase.NIGHT:
                return False
                
        return True
        
    def check(self, target_id: str, game_state: Dict[str, Any]) -> bool:
        """执行查验行动
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 查验是否成功
        """
        if not self.can_check(target_id, game_state):
            return False
            
        # 检查目标是否存活
        if target_id not in game_state['alive_players']:
            return False
            
        # 获取目标角色信息
        target = game_state['players'][target_id]
        target_role = target.role.get_role_name()
        target_team = str(target.role.get_team())
        
        # 格式化查验结果
        self.last_check_result = {
            'target': target_id,
            'role': target_role,
            'team': target_team,
            'formatted': self.config['SEER_CONFIG']['result_format'].format(
                target=target_id,
                role=target_role,
                team=target_team
            )
        }
        
        # 更新查验次数和冷却
        self.check_count += 1
        self.use_skill('check')
        
        return True
        
    def get_check_result(self) -> Optional[Dict[str, Any]]:
        """获取查验结果
        
        Returns:
            Optional[Dict[str, Any]]: 查验结果字典，如果没有结果则返回None
        """
        return self.last_check_result
        
    def update_cooldowns(self, current_phase: GamePhase):
        """更新技能冷却
        
        Args:
            current_phase: 当前游戏阶段
        """
        super().update_cooldowns(current_phase)
        # 在白天阶段清除上次查验结果
        if current_phase == GamePhase.DAY_DISCUSSION:
            self.last_check_result = None
            
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'seer',
            'team': str(self.team),
            'check_count': self.check_count,
            'last_check_result': self.last_check_result,
            'cooldowns': self.cooldowns.copy()
        } 