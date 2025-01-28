from typing import Dict, Any, Optional
from .base_role import BaseRole
from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class Witch(BaseRole):
    """女巫角色类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        super().__init__(player_id, config)
        self.team = Team.VILLAGER
        self.has_heal_potion = True  # 是否有救药
        self.has_poison_potion = True  # 是否有毒药
        self.last_heal_target = None  # 上次救治目标
        self.last_poison_target = None  # 上次毒杀目标
        
        # 确保WITCH_CONFIG存在
        if 'WITCH_CONFIG' not in self.config:
            self.config['WITCH_CONFIG'] = {}
        # 设置默认值
        self.config['WITCH_CONFIG'].setdefault('can_save_self', False)  # 默认不能自救
        self.config['WITCH_CONFIG'].setdefault('poison_priority', 1)  # 毒药优先级
        self.config['WITCH_CONFIG'].setdefault('night_only', True)  # 只能在夜晚使用技能
        self.config['WITCH_CONFIG'].setdefault('heal_count', 1)  # 救药次数限制
        self.config['WITCH_CONFIG'].setdefault('poison_count', 1)  # 毒药次数限制
        
    def can_heal(self, target_id: str) -> bool:
        """检查是否可以救治目标
        
        Args:
            target_id: 目标玩家ID
            
        Returns:
            bool: 是否可以救治
        """
        # 检查基本条件
        if not self.can_use_skill('heal'):
            return False
            
        # 检查是否有救药
        if not self.has_heal_potion:
            return False
            
        # 检查是否可以自救
        if target_id == self.player_id and not self.config['WITCH_CONFIG']['can_save_self']:
            return False
            
        return True
        
    def can_poison(self, target_id: str) -> bool:
        """检查是否可以毒杀目标
        
        Args:
            target_id: 目标玩家ID
            
        Returns:
            bool: 是否可以毒杀
        """
        # 检查基本条件
        if not self.can_use_skill('poison'):
            return False
            
        # 检查是否有毒药
        if not self.has_poison_potion:
            return False
            
        # 不能毒杀自己
        if target_id == self.player_id:
            return False
            
        return True
        
    def heal(self, target_id: str, game_state: Dict[str, Any]) -> bool:
        """执行救治行动
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 救治是否成功
        """
        if not self.can_heal(target_id):
            return False
            
        # 检查目标是否在夜晚死亡列表中
        if target_id not in game_state.get('night_deaths', set()):
            return False
            
        # 从死亡列表中移除
        game_state['night_deaths'].remove(target_id)
        
        # 记录救治
        self.last_heal_target = target_id
        self.has_heal_potion = False
        self.use_skill('heal')
        
        return True
        
    def poison(self, target_id: str, game_state: Dict[str, Any]) -> bool:
        """执行毒杀行动
        
        Args:
            target_id: 目标玩家ID
            game_state: 游戏状态
            
        Returns:
            bool: 毒杀是否成功
        """
        if not self.can_poison(target_id):
            return False
            
        # 检查目标是否存活
        if target_id not in game_state['alive_players']:
            return False
            
        # 检查目标是否被守护
        target = game_state['players'][target_id]
        if target.status['protected']:
            return False
            
        # 记录毒杀
        self.last_poison_target = target_id
        self.has_poison_potion = False
        game_state.setdefault('night_deaths', set()).add(target_id)
        self.use_skill('poison')
        
        return True
        
    def update_cooldowns(self, current_phase: GamePhase):
        """更新技能冷却
        
        Args:
            current_phase: 当前游戏阶段
        """
        super().update_cooldowns(current_phase)
        # 在白天阶段重置上次行动记录
        if current_phase == GamePhase.DAY_DISCUSSION:
            self.last_heal_target = None
            self.last_poison_target = None
            
    def get_role_info(self) -> Dict[str, Any]:
        """获取角色信息
        
        Returns:
            Dict[str, Any]: 角色信息字典
        """
        return {
            'role': 'witch',
            'team': str(self.team),
            'has_heal_potion': self.has_heal_potion,
            'has_poison_potion': self.has_poison_potion,
            'last_heal_target': self.last_heal_target,
            'last_poison_target': self.last_poison_target,
            'cooldowns': self.cooldowns.copy()
        } 