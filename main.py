import argparse
import threading
from pathlib import Path

from core.engine.game_loop import GameLoop
from config.game_config import PHASE_CONFIG, ROLE_COOLDOWNS
from services.game_state_store import GameStateStore
from utils.logger import logger



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="狼人杀AI对战模拟")
    parser.add_argument("--web", action="store_true", help="启动观战Web界面")
    parser.add_argument("--web-host", default="127.0.0.1", help="Web服务绑定地址")
    parser.add_argument("--web-port", type=int, default=8000, help="Web服务端口")
    parser.add_argument(
        "--web-static-dir",
        type=Path,
        default=None,
        help="自定义静态文件目录（默认使用内置页面）",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

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

    state_store = GameStateStore() if args.web else None

    if args.web and state_store is not None:
        from interfaces.http.api import run_app

        static_dir = (args.web_static_dir or (Path(__file__).resolve().parent / "interfaces/http/static")).resolve()
        web_thread = threading.Thread(
            target=run_app,
            args=(state_store,),
            kwargs={
                'host': args.web_host,
                'port': args.web_port,
                'static_dir': static_dir,
            },
            daemon=True,
        )
        web_thread.start()
        logger.info(f"观战面板已启动，监听 {args.web_host}:{args.web_port}")

    # 狼人杀标准局12人:
    # 3狼人、1预言家、1女巫、1猎人、1守卫、5平民
    game = GameLoop(config, state_store=state_store)
    game.initialize_game(players)
    game.run()
