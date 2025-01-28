from core.engine.phase_manager import GamePhase

PHASE_CONFIG = {
    GamePhase.DAY_DISCUSSION: {
        'duration': 5,  # 秒
        'order': 1,
        'description': "白天讨论阶段"
    },
    GamePhase.DAY_VOTE: {
        'duration': 5,
        'order': 2,
        'description': "投票阶段"
    },
    GamePhase.NIGHT: {
        'duration': 5,
        'order': 0,
        'description': "夜晚行动阶段"
    }
}

NEUTRAL_VICTORY_CONDITIONS = {
    'min_players': 2,
    'required_survival_rate': 0.8
}

THIEF_CONFIG = {
    'stealable_roles': ['werewolf', 'seer', 'witch', 'hunter'],
    'must_steal': True  # 是否必须偷换角色
}

ROLE_COOLDOWNS = {
    'werewolf': {'kill': 0},
    'seer': {'check': 1},
    'witch': {'heal': 3, 'poison': 0},
    'hunter': {'shoot': 1},
    'guard': {'protect': 1},
    'fool': {'reveal': 999},
    'thief': {'steal': 999},
    'cupid': {'match': 999}
}

SEER_CONFIG = {
    'max_checks': 3,
    'result_format': "{target} => {role} ({team})",
    'allow_self_check': False,
    'night_only': True
}

CUPID_CONFIG = {
    'max_matches': 1  # 最大匹配次数
}

FOOL_CONFIG = { 
    'reveal_immunity': 2  # 抗票次数
}

WEREWOLF_CONFIG = {
    'night_kill_limit': 1  # 每夜最多击杀数
}

GUARD_CONFIG = {
    'consecutive_protection': False  # 是否允许连续守护同一玩家
} 