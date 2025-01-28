from typing import Dict, Any, Optional
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Guard(BaseRole):
    """守卫角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.VILLAGER
        self.protect_count = 0  # 守护次数
        self.last_protected = None  # 上次守护目标
        
        # 确保GUARD_CONFIG存在
        if 'GUARD_CONFIG' not in self.config:
            self.config['GUARD_CONFIG'] = {}
        # 设置默认值
        self.config['GUARD_CONFIG'].setdefault('max_protects', 999)  # 最大守护次数
        self.config['GUARD_CONFIG'].setdefault('consecutive_protection', False)  # 是否允许连续守护同一目标
        self.config['GUARD_CONFIG'].setdefault('can_protect_self', False)  # 是否可以守护自己
        self.config['GUARD_CONFIG'].setdefault('night_only', True)  # 只能在夜晚守护
        
    def can_protect(self, target_id: str) -> bool:
        """检查是否可以守护目标
        
        Args:
            target_id: 目标玩家ID
            
        Returns:
            bool: 是否可以守护
        """
        # 检查基本条件
        if not self.can_use_skill('protect'):
            return False
            
        # 检查守护次数限制
        if self.protect_count >= self.config['GUARD_CONFIG']['max_protects']:
            return False
            
        # 检查是否允许连续守护同一目标
        if not self.config['GUARD_CONFIG']['consecutive_protection']:
            if target_id == self.last_protected:
                return False
                
        return True
        
    def protect(self, target_id: str, game_state: Dict[str, Any]) -> bool:
        """执行守护行动
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 守护是否成功
        """
        if not self.can_protect(target_id):
            return False
            
        # 检查目标是否存活
        if target_id not in game_state['alive_players']:
            return False
            
        # 记录守护
        target = game_state['players'][target_id]
        target.status['protected'] = True
        self.last_protected = target_id
        self.protect_count += 1
        self.use_skill('protect')
        
        return True
        
    def update_cooldowns(self, current_phase: GamePhase):
        """更新技能冷却
        
        Args:
            current_phase: 当前游戏阶段
        """
        super().update_cooldowns(current_phase)
        # 在白天阶段移除所有守护状态
        if current_phase == GamePhase.DAY_DISCUSSION:
            self.last_protected = None
            # 重置守护状态
            if hasattr(self, 'game_state') and self.game_state:
                for player in self.game_state['players'].values():
                    player.status['protected'] = False
            
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'guard',
            'team': str(self.team),
            'protect_count': self.protect_count,
            'last_protected': self.last_protected,
            'cooldowns': self.cooldowns.copy()
        } 