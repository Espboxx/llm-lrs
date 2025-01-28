from core.engine.game_loop import GameLoop
from config.game_config import PHASE_CONFIG, ROLE_COOLDOWNS

if __name__ == "__main__":
    players = [f"player{i}" for i in range(1, 13)]  # 12人局
    
    config = {
        'PHASE_CONFIG': PHASE_CONFIG,
        'ROLE_COOLDOWNS': ROLE_COOLDOWNS,
        'SEER_CONFIG': {
            'max_checks': 3,
            'allow_self_check': False
        },
        'ROLE_DISTRIBUTION': {
            'werewolf': 3,
            'villager': 5,
            'seer': 1,
            'witch': 1,
            'hunter': 1,
            'guard': 1
        },
        'WITCH_CONFIG': {
            'can_save_self': True,
            'poison_priority': 1
        },
        'HUNTER_CONFIG': {
            'can_shoot_dead': True
        },
        'GUARD_CONFIG': {
            'max_protects': 3
        },
        'players': players  # 新增玩家列表
    }
    
    # 狼人杀标准局12人:
    # 3狼人、1预言家、1女巫、1猎人、1守卫、5平民
    game = GameLoop(config)
    game.initialize_game(players)
    game.run()