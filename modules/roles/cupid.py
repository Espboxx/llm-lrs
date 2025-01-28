from typing import Dict, Any, Optional, List, Tuple
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Cupid(BaseRole):
    """丘比特角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.NEUTRAL
        self.match_count = 0  # 匹配次数
        self.matched_pairs: List[Tuple[str, str]] = []  # 已匹配的情侣
        
    def can_match(self, player1_id: str, player2_id: str) -> bool:
        """检查是否可以匹配两个玩家
        
        Args:
            player1_id: 第一个玩家ID
            player2_id: 第二个玩家ID
            
        Returns:
            bool: 是否可以匹配
        """
        # 检查基本条件
        if not self.can_use_skill('match'):
            return False
            
        # 检查匹配次数限制
        if self.match_count >= self.config['CUPID_CONFIG']['max_matches']:
            return False
            
        # 检查是否是同一个玩家
        if player1_id == player2_id:
            return False
            
        # 检查玩家是否已经被匹配
        matched_players = {p for pair in self.matched_pairs for p in pair}
        if player1_id in matched_players or player2_id in matched_players:
            return False
            
        return True
        
    def match(self, player1_id: str, player2_id: str, game_state: Dict[str, Any]) -> bool:
        """执行匹配行动
        
        Args:
            player1_id: 第一个玩家ID
            player2_id: 第二个玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 匹配是否成功
        """
        if not self.can_match(player1_id, player2_id):
            return False
            
        # 检查玩家是否存活
        if (player1_id not in game_state['alive_players'] or
            player2_id not in game_state['alive_players']):
            return False
            
        # 记录匹配
        self.matched_pairs.append((player1_id, player2_id))
        self.match_count += 1
        
        # 更新玩家阵营
        player1 = game_state['players'][player1_id]
        player2 = game_state['players'][player2_id]
        player1.role.set_team(Team.LOVERS)
        player2.role.set_team(Team.LOVERS)
        
        # 重置技能冷却
        self.use_skill('match')
        
        return True
        
    def handle_death(self, game_loop):
        """处理死亡事件
        
        Args:
            game_loop: 游戏循环实例
        """
        super().handle_death(game_loop)
        
        # 检查情侣是否需要殉情
        for player1_id, player2_id in self.matched_pairs:
            player1 = game_loop.game_state['players'][player1_id]
            player2 = game_loop.game_state['players'][player2_id]
            
            # 如果一个情侣死亡，另一个也要死亡
            if not player1.status['alive'] and player2.status['alive']:
                game_loop.message_router.broadcast(
                    f"玩家 {player2_id} 因情侣 {player1_id} 死亡而殉情",
                    channel="system",
                    recipients=game_loop.game_state['alive_players']
                )
                game_loop.game_state.setdefault(
                    'night_deaths' if game_loop.game_state['current_phase'] == GamePhase.NIGHT
                    else 'day_deaths',
                    set()
                ).add(player2_id)
            elif not player2.status['alive'] and player1.status['alive']:
                game_loop.message_router.broadcast(
                    f"玩家 {player1_id} 因情侣 {player2_id} 死亡而殉情",
                    channel="system",
                    recipients=game_loop.game_state['alive_players']
                )
                game_loop.game_state.setdefault(
                    'night_deaths' if game_loop.game_state['current_phase'] == GamePhase.NIGHT
                    else 'day_deaths',
                    set()
                ).add(player1_id)
                
    def get_matched_pairs(self) -> List[Tuple[str, str]]:
        """获取已匹配的情侣列表
        
        Returns:
            List[Tuple[str, str]]: 情侣对列表
        """
        return self.matched_pairs.copy()
        
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'cupid',
            'team': str(self.team),
            'match_count': self.match_count,
            'matched_pairs': self.matched_pairs.copy(),
            'cooldowns': self.cooldowns.copy()
        } 