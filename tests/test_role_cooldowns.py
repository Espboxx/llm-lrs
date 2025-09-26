import copy

import pytest

from modules.roles.role_factory import RoleFactory
from config.game_config import (
    ROLE_COOLDOWNS,
    SEER_CONFIG,
    GUARD_CONFIG,
    THIEF_CONFIG,
    CUPID_CONFIG,
    FOOL_CONFIG,
    WEREWOLF_CONFIG,
)


OPTIONAL_ROLE_CONFIGS = {
    'SEER_CONFIG': SEER_CONFIG,
    'GUARD_CONFIG': GUARD_CONFIG,
    'THIEF_CONFIG': THIEF_CONFIG,
    'CUPID_CONFIG': CUPID_CONFIG,
    'FOOL_CONFIG': FOOL_CONFIG,
    'WEREWOLF_CONFIG': WEREWOLF_CONFIG,
}


def build_role_config():
    """构造角色配置，避免实例化时缺少必需条目"""
    config = {'ROLE_COOLDOWNS': copy.deepcopy(ROLE_COOLDOWNS)}
    for key, value in OPTIONAL_ROLE_CONFIGS.items():
        config[key] = copy.deepcopy(value)
    config['WITCH_CONFIG'] = {}
    config['HUNTER_CONFIG'] = {}
    return config


@pytest.mark.parametrize('role_name', ROLE_COOLDOWNS.keys())
def test_all_roles_start_with_zero_cooldown(role_name):
    config = build_role_config()
    role = RoleFactory.create_role(role_name, 'tester', config)

    for skill, expected_default in ROLE_COOLDOWNS[role_name].items():
        assert role.cooldowns[skill] == 0
        assert role.cooldown_defaults[skill] == expected_default
