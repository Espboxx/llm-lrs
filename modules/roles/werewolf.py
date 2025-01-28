from typing import Dict, Any, Optional, List
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Werewolf(BaseRole):
    """狼人角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.WEREWOLF
        self.night_kill_count = 0  # 记录击杀次数
        self.last_kill_target = None  # 记录上次击杀目标
        
        # 确保WEREWOLF_CONFIG存在
        if 'WEREWOLF_CONFIG' not in self.config:
            self.config['WEREWOLF_CONFIG'] = {}
        # 设置默认值
        self.config['WEREWOLF_CONFIG'].setdefault('night_kill_limit', 1)  # 每晚最多击杀1人
        self.config['WEREWOLF_CONFIG'].setdefault('can_kill_self', False)  # 不能击杀自己
        self.config['WEREWOLF_CONFIG'].setdefault('night_only', True)  # 只能在夜晚击杀
        
    def can_kill(self, target_id: str) -> bool:
        """检查是否可以击杀目标
        
        Args:
            target_id: 目标玩家ID
            
        Returns:
            bool: 是否可以击杀
        """
        # 检查基本条件
        if not self.can_use_skill('kill'):
            return False
            
        # 检查击杀次数限制
        if self.night_kill_count >= self.config['WEREWOLF_CONFIG']['night_kill_limit']:
            return False
            
        # 不能击杀自己
        if target_id == self.player_id and not self.config['WEREWOLF_CONFIG']['can_kill_self']:
            return False
            
        return True
        
    def kill(self, target_id: str, game_state: Dict[str, Any]) -> bool:
        """执行击杀行动
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 击杀是否成功
        """
        if not self.can_kill(target_id):
            return False
            
        # 检查目标是否存活
        if target_id not in game_state['alive_players']:
            return False
            
        # 检查目标是否被守护
        target = game_state['players'][target_id]
        if target.status['protected']:
            return False
            
        # 记录击杀
        self.night_kill_count += 1
        self.last_kill_target = target_id
        game_state.setdefault('night_deaths', set()).add(target_id)
        
        # 重置技能冷却
        self.use_skill('kill')
        
        return True
        
    def get_fellow_wolves(self, game_state: Dict[str, Any]) -> List[str]:
        """获取其他存活的狼人
        
        Args:
            game_state: 游戏状态
            
        Returns:
            List[str]: 其他存活狼人的ID列表
        """
        return [
            pid for pid in game_state['alive_players']
            if pid != self.player_id and
            isinstance(game_state['players'][pid].role, Werewolf)
        ]
        
    def update_cooldowns(self, current_phase: GamePhase):
        """更新技能冷却
        
        Args:
            current_phase: 当前游戏阶段
        """
        super().update_cooldowns(current_phase)
        # 在白天阶段重置击杀计数
        if current_phase == GamePhase.DAY_DISCUSSION:
            self.night_kill_count = 0
            self.last_kill_target = None
            
    def handle_death(self, game_loop):
        """处理死亡事件
        
        Args:
            game_loop: 游戏循环实例
        """
        super().handle_death(game_loop)
        # 通知其他狼人
        for wolf_id in self.get_fellow_wolves(game_loop.game_state):
            game_loop.message_router.broadcast(
                f"你的同伴 {self.player_id} 已死亡",
                channel="werewolf",
                recipients=[wolf_id]
            )
            
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'werewolf',
            'team': str(self.team),
            'night_kill_count': self.night_kill_count,
            'last_kill_target': self.last_kill_target,
            'cooldowns': self.cooldowns.copy()
        } 