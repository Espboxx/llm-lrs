from typing import Dict, Any, Optional

from core.engine.victory_checker import Team
from core.engine.phase_manager import GamePhase

class BaseRole:
    """角色基类"""
    
    def __init__(self, player_id: str, config: Dict[str, Any]):
        self.player_id = player_id
        self.config = config
        self.team = Team.UNKNOWN
        self.status = {
            'alive': True,
            'protected': False,
            'silenced': False,
            'poisoned': False
        }
        self.cooldowns: Dict[str, int] = {}  # 技能当前冷却
        self.cooldown_defaults: Dict[str, int] = {}  # 技能冷却配置值
        self.game_state = None  # 初始化游戏状态为None
        self._initialize_cooldowns()  # 初始化技能冷却
        
    def _initialize_cooldowns(self):
        """初始化技能冷却"""
        role_name = self.__class__.__name__.lower()
        role_cooldowns = self.config.get('ROLE_COOLDOWNS', {}).get(role_name)
        if role_cooldowns:
            self.cooldown_defaults = role_cooldowns.copy()
            self.cooldowns = {skill: 0 for skill in role_cooldowns}
            
    def update_cooldowns(self, current_phase: GamePhase):
        """更新技能冷却
        
        Args:
            current_phase: 当前游戏阶段
        """
        for skill in self.cooldowns:
            if self.cooldowns[skill] > 0:
                self.cooldowns[skill] -= 1
                
    def can_use_skill(self, skill_name: str) -> bool:
        """检查是否可以使用技能
        
        Args:
            skill_name: 技能名称
            
        Returns:
            bool: 是否可以使用技能
        """
        # 检查是否存活
        if not self.status['alive']:
            return False
            
        # 检查是否被禁言
        if self.status['silenced']:
            return False
            
        # 检查冷却
        if skill_name in self.cooldowns and self.cooldowns[skill_name] > 0:
            return False
            
        return True
        
    def use_skill(self, skill_name: str, target_id: Optional[str] = None) -> bool:
        """使用技能，重置冷却
        
        Args:
            skill_name: 技能名称
            target_id: 目标玩家ID（可选）
        
        Returns:
            bool: 技能是否使用成功
        """
        if not self.can_use_skill(skill_name):
            return False
                
        # 重置技能冷却
        default_cooldown = self.cooldown_defaults.get(skill_name)
        if default_cooldown is not None:
            self.cooldowns[skill_name] = default_cooldown
        else:
            self.cooldowns[skill_name] = 0

        return True
        
    def handle_death(self, game_loop):
        """处理角色死亡
        
        Args:
            game_loop: 游戏循环实例
        """
        self.status['alive'] = False
        
    def get_role_name(self) -> str:
        """获取角色名称"""
        return self.__class__.__name__.lower()
        
    def get_team(self) -> Team:
        """获取角色阵营"""
        return self.team
        
    def set_team(self, new_team: Team):
        """设置角色阵营
        
        Args:
            new_team: 新阵营
        """
        self.team = new_team
        
    def is_alive(self) -> bool:
        """检查角色是否存活"""
        return self.status['alive']
        
    def protect(self):
        """守护角色"""
        self.status['protected'] = True
        
    def unprotect(self):
        """移除守护状态"""
        self.status['protected'] = False
        
    def silence(self):
        """沉默角色"""
        self.status['silenced'] = True
        
    def unsilence(self):
        """解除沉默"""
        self.status['silenced'] = False
        
    def poison(self):
        """毒杀角色"""
        self.status['poisoned'] = True
        
    def heal(self):
        """治疗角色"""
        self.status['poisoned'] = False
        
    def set_game_state(self, game_state: Dict[str, Any]):
        """设置游戏状态
        
        Args:
            game_state: 游戏状态字典
        """
        self.game_state = game_state