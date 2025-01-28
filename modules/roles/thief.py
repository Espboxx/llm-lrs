from typing import Dict, Any, Optional, List
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Thief(BaseRole):
    """盗贼角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.NEUTRAL
        self.has_stolen = False  # 是否已经偷取角色
        self.stolen_role = None  # 偷取的角色
        self.cooldowns = {
            'steal': config.get('ROLE_COOLDOWNS', {}).get('thief', {}).get('steal', 999)
        }
        
    def can_steal(self, role_name: str) -> bool:
        """检查是否可以偷取角色
        
        Args:
            role_name: 目标角色名称
            
        Returns:
            bool: 是否可以偷取
        """
        # 检查基本条件
        if not self.can_use_skill('steal'):
            return False
            
        # 检查是否已经偷取过
        if self.has_stolen:
            return False
            
        # 检查角色是否在可偷取列表中
        if role_name not in self.config['THIEF_CONFIG']['stealable_roles']:
            return False
            
        return True
        
    def steal(self, role_name: str, game_state: Dict[str, Any]) -> bool:
        """执行偷取行动
        
        Args:
            role_name: 目标角色名称
            game_state: 游戏状态
            
        Returns:
            bool: 偷取是否成功
        """
        if not self.can_steal(role_name):
            return False
            
        # 记录偷取
        self.stolen_role = role_name
        self.has_stolen = True
        self.use_skill('steal')
        
        return True
        
    def get_stealable_roles(self) -> List[str]:
        """获取可偷取的角色列表
        
        Returns:
            List[str]: 可偷取的角色名称列表
        """
        return self.config['THIEF_CONFIG']['stealable_roles']
        
    def handle_timeout(self, game_loop):
        """处理超时未选择
        
        Args:
            game_loop: 游戏循环实例
        """
        if not self.has_stolen and self.config['THIEF_CONFIG']['must_steal']:
            # 随机选择一个角色
            import random
            available_roles = self.get_stealable_roles()
            if available_roles:
                role = random.choice(available_roles)
                self.steal(role, game_loop.game_state)
                game_loop.message_router.broadcast(
                    f"盗贼 {self.player_id} 超时，随机选择了 {role} 角色",
                    channel="system",
                    recipients=game_loop.game_state['alive_players']
                )
                
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'thief',
            'team': str(self.team),
            'has_stolen': self.has_stolen,
            'stolen_role': self.stolen_role,
            'cooldowns': self.cooldowns.copy()
        } 