from modules.roles.base_role import BaseRole
from typing import Dict
from modules.roles.werewolf import Werewolf
from modules.roles.seer import Seer
from modules.roles.villager import Villager
from modules.roles.witch import Witch
from modules.roles.hunter import Hunter
from modules.roles.guard import Guard
from modules.roles.fool import Fool
from modules.roles.thief import Thief
from modules.roles.cupid import Cupid

class RoleFactory:
    """角色工厂"""
    ROLE_MAP = {
        'werewolf': lambda: Werewolf,
        'seer': lambda: Seer,
        'villager': lambda: Villager,
        'witch': lambda: Witch,
        'hunter': lambda: Hunter,
        'guard': lambda: Guard,
        'fool': lambda: Fool,
        'thief': lambda: Thief,
        'cupid': lambda: Cupid
    }

    @classmethod
    def create_role(cls, role_name: str, player_id: str, config: dict) -> BaseRole:
        """统一创建角色方法"""
        role_class = cls.ROLE_MAP.get(role_name.lower(), lambda: Villager)()
        return role_class(player_id, config)

    @classmethod
    def assign_roles(cls, players: list) -> Dict[str, str]:
        """根据配置分配角色"""
        # 需要从config读取角色分布
        return {p: 'villager' for p in players}  # 示例实现 