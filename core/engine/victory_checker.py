from enum import Enum, auto
from typing import Dict, Set, Optional

class Team(Enum):
    """游戏阵营"""
    UNKNOWN = auto()  # 未知阵营
    VILLAGER = auto()  # 村民阵营
    WEREWOLF = auto()  # 狼人阵营
    LOVERS = auto()  # 情侣阵营
    NEUTRAL = auto()  # 中立阵营

class VictoryChecker:
    """胜利条件检查器"""
    def __init__(self):
        self.players: Dict[str, Team] = {}  # 玩家ID -> 阵营
        self.alive_players: Set[str] = set()  # 存活玩家ID集合
        self.dead_players: Set[str] = set()   # 死亡玩家ID集合
        
    def register_player(self, player_id: str, team: Team):
        """注册玩家及其阵营
        
        Args:
            player_id: 玩家ID
            team: 玩家所属阵营
        """
        self.players[player_id] = team
        self.alive_players.add(player_id)
        
    def remove_player(self, player_id: str):
        """移除玩家（死亡）
        
        Args:
            player_id: 玩家ID
        """
        if player_id in self.alive_players:
            self.alive_players.remove(player_id)
            self.dead_players.add(player_id)
            
    def get_alive_players(self) -> Set[str]:
        """获取存活玩家列表"""
        return self.alive_players.copy()
        
    def get_dead_players(self) -> Set[str]:
        """获取死亡玩家列表"""
        return self.dead_players.copy()
        
    def check_victory(self, game_state: Optional[Dict] = None) -> Optional[Team]:
        """检查是否有阵营胜利
        
        Args:
            game_state: 游戏状态字典（可选）
            
        Returns:
            Optional[Team]: 胜利阵营，如果没有胜利则返回None
        """
        # 统计存活玩家阵营
        alive_teams = {
            team: sum(1 for pid in self.alive_players if self.players[pid] == team)
            for team in Team
        }
        
        # 情侣胜利条件：所有情侣存活且其他玩家全部死亡
        if alive_teams[Team.LOVERS] >= 2 and sum(
            count for team, count in alive_teams.items()
            if team != Team.LOVERS
        ) == 0:
            return Team.LOVERS
            
        # 狼人胜利条件：狼人数量大于等于好人数量
        villager_count = alive_teams[Team.VILLAGER]
        werewolf_count = alive_teams[Team.WEREWOLF]
        if werewolf_count >= villager_count and werewolf_count > 0:
            return Team.WEREWOLF
            
        # 好人胜利条件：所有狼人死亡且有好人存活
        if werewolf_count == 0 and villager_count > 0:
            return Team.VILLAGER
            
        # 中立阵营胜利条件（如果有配置）
        if game_state and 'NEUTRAL_VICTORY_CONDITIONS' in game_state['config']:
            neutral_config = game_state['config']['NEUTRAL_VICTORY_CONDITIONS']
            neutral_count = alive_teams[Team.NEUTRAL]
            
            # 检查存活人数是否达到要求
            if neutral_count >= neutral_config['min_players']:
                # 检查存活率是否达到要求
                total_alive = sum(alive_teams.values())
                if neutral_count / total_alive >= neutral_config['required_survival_rate']:
                    return Team.NEUTRAL
                    
        return None  # 没有阵营达成胜利条件
        
    def get_winner(self) -> Optional[Team]:
        """获取胜利阵营"""
        return self.check_victory()
        
    def get_team_players(self, team: Team) -> Set[str]:
        """获取指定阵营的所有玩家
        
        Args:
            team: 目标阵营
            
        Returns:
            Set[str]: 该阵营的玩家ID集合
        """
        return {
            pid for pid, t in self.players.items()
            if t == team
        }
        
    def get_player_team(self, player_id: str) -> Optional[Team]:
        """获取玩家所属阵营
        
        Args:
            player_id: 玩家ID
            
        Returns:
            Optional[Team]: 玩家所属阵营，如果玩家不存在则返回None
        """
        return self.players.get(player_id)
        
    def change_player_team(self, player_id: str, new_team: Team):
        """更改玩家阵营
        
        Args:
            player_id: 玩家ID
            new_team: 新阵营
        """
        if player_id in self.players:
            self.players[player_id] = new_team 