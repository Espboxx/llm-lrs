from typing import Dict, Any, Optional
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Fool(BaseRole):
    """白痴角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.VILLAGER
        self.reveal_count = 0  # 抗投票次数
        self.revealed = False  # 是否已经暴露身份
        
    def can_reveal(self) -> bool:
        """检查是否可以暴露身份
        
        Returns:
            bool: 是否可以暴露
        """
        # 检查基本条件
        if not self.can_use_skill('reveal'):
            return False
            
        # 检查是否已经暴露过
        if self.revealed:
            return False
            
        # 检查是否还有抗投票次数
        if self.reveal_count >= self.config['FOOL_CONFIG']['reveal_immunity']:
            return False
            
        return True
        
    def reveal(self, game_state: Dict[str, Any]) -> bool:
        """执行暴露身份行动
        
        Args:
            game_state: 游戏状态
            
        Returns:
            bool: 暴露是否成功
        """
        if not self.can_reveal():
            return False
            
        # 记录暴露
        self.revealed = True
        self.reveal_count += 1
        self.use_skill('reveal')
        
        return True
        
    def handle_vote(self, game_loop) -> bool:
        """处理被投票事件
        
        Args:
            game_loop: 游戏循环实例
            
        Returns:
            bool: 是否免疫死亡
        """
        # 如果还没暴露身份，现在暴露
        if not self.revealed and self.can_reveal():
            self.reveal(game_loop.game_state)
            game_loop.message_router.broadcast(
                f"玩家 {self.player_id} 是白痴，免疫本次投票",
                channel="system",
                recipients=game_loop.game_state['alive_players']
            )
            return True
            
        return False
        
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'fool',
            'team': str(self.team),
            'reveal_count': self.reveal_count,
            'revealed': self.revealed,
            'cooldowns': self.cooldowns.copy()
        } 