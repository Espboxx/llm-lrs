from typing import Dict, Any
from .base_role import BaseRole
from core.engine.victory_checker import Team

class Villager(BaseRole):
    """村民角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.VILLAGER
        # 村民没有主动技能，保留基础冷却系统
        self.cooldowns = {} 

    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'villager',
            'team': str(self.team),
            'cooldowns': self.cooldowns.copy()
        } 