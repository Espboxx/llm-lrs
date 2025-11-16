import argparse
import threading
from pathlib import Path
from typing import Optional

from config.game_config import PHASE_CONFIG, ROLE_COOLDOWNS
from services.game_controller import GameController
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
    )
    parser.add_argument(
        "--auto-start",
        action="store_true",
        help="启动后自动开局（web模式默认等待前端触发）",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    players = [f"player{i}" for i in range(1, 13)]  # 12人局

    base_config = {
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
        'players': players,
    }

    state_store = GameStateStore() if args.web else None
    controller = GameController(
        base_config=base_config,
        players=players,
        state_store=state_store,
        save_dir=Path(__file__).resolve().parent / "logs" / "saves",
    )

    web_thread: Optional[threading.Thread] = None
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
                'controller': controller,
            },
            daemon=True,
        )
        web_thread.start()
        logger.info(f"观战面板已启动，监听 {args.web_host}:{args.web_port}")

    try:
        if not args.web or args.auto_start:
            logger.info("自动启动一局狼人杀对局")
            controller.start()
            if not args.web:
                controller.wait_for_completion()
        if args.web and web_thread is not None:
            web_thread.join()
    except KeyboardInterrupt:
        logger.info("收到中断信号，准备停止对局")
        controller.stop()
    finally:
        controller.wait_for_completion()
