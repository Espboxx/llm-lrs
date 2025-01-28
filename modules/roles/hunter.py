from typing import Dict, Any, Optional
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Hunter(BaseRole):
    """猎人角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.VILLAGER
        self.has_shot = False  # 是否已经开枪
        self.last_shot_target = None  # 上次射击目标
        
        # 确保HUNTER_CONFIG存在
        if 'HUNTER_CONFIG' not in self.config:
            self.config['HUNTER_CONFIG'] = {}
        # 设置默认值
        self.config['HUNTER_CONFIG'].setdefault('can_shoot_dead', True)  # 死亡时是否可以开枪
        self.config['HUNTER_CONFIG'].setdefault('can_shoot_self', False)  # 是否可以射击自己
        self.config['HUNTER_CONFIG'].setdefault('shot_count', 1)  # 开枪次数限制
        self.config['HUNTER_CONFIG'].setdefault('night_only', False)  # 不限定只能在夜晚开枪
        
    def can_shoot(self, target_id: str) -> bool:
        """检查是否可以射击目标
        
        Args:
            target_id: 目标玩家ID
            
        Returns:
            bool: 是否可以射击
        """
        # 检查基本条件
        if not self.can_use_skill('shoot'):
            return False
            
        # 检查是否已经开过枪
        if self.has_shot:
            return False
            
        # 检查是否可以在死亡时开枪
        if not self.status['alive'] and not self.config['HUNTER_CONFIG']['can_shoot_dead']:
            return False
            
        # 不能射击自己
        if target_id == self.player_id:
            return False
            
        return True
        
    def shoot(self, target_id: str, game_state: Dict[str, Any]) -> bool:
        """执行射击行动
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 射击是否成功
        """
        if not self.can_shoot(target_id):
            return False
            
        # 检查目标是否存活
        if target_id not in game_state['alive_players']:
            return False
            
        # 检查目标是否被守护
        target = game_state['players'][target_id]
        if target.status['protected']:
            return False
            
        # 记录射击
        self.last_shot_target = target_id
        self.has_shot = True
        game_state.setdefault('night_deaths' if game_state['current_phase'] == GamePhase.NIGHT else 'day_deaths', set()).add(target_id)
        self.use_skill('shoot')
        
        return True
        
    def handle_death(self, game_loop):
        """处理死亡事件
        
        Args:
            game_loop: 游戏循环实例
        """
        super().handle_death(game_loop)
        
        # 如果配置允许死亡时开枪，添加到待处理动作
        if not self.has_shot and self.config['HUNTER_CONFIG']['can_shoot_dead']:
            game_loop.message_router.broadcast(
                f"猎人 {self.player_id} 死亡，可以开枪带走一个人",
                channel="system",
                recipients=game_loop.game_state['alive_players']
            )
            # 等待猎人选择目标
            target = self._get_shot_target(game_loop.game_state)
            if target:
                self.shoot(target, game_loop.game_state)
                
    def _get_shot_target(self, game_state: Dict[str, Any]) -> Optional[str]:
        """获取射击目标（示例实现）
        
        Args:
            game_state: 游戏状态
            
        Returns:
            Optional[str]: 目标玩家ID，如果没有合适目标则返回None
        """
        # 这里应该实现获取玩家选择的逻辑
        # 示例中简单返回第一个存活玩家
        alive_players = [
            pid for pid in game_state['alive_players']
            if pid != self.player_id
        ]
        return alive_players[0] if alive_players else None
        
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'hunter',
            'team': str(self.team),
            'has_shot': self.has_shot,
            'last_shot_target': self.last_shot_target,
            'cooldowns': self.cooldowns.copy()
        } 