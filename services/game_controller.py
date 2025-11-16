from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from utils.logger import logger
from core.engine.game_loop import GameLoop
from services.game_state_store import GameStateStore


class GameController:
    """管理游戏生命周期，提供启动/暂停/保存等能力。"""

    def __init__(
        self,
        *,
        base_config: Dict[str, Any],
        players: List[str],
        state_store: Optional[GameStateStore] = None,
        save_dir: Optional[Path] = None,
    ) -> None:
        self._base_config = deepcopy(base_config)
        self._players_template = list(players)
        self._state_store = state_store
        self._save_dir = Path(save_dir or Path("logs") / "saves")
        self._save_dir.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._game: Optional[GameLoop] = None
        self._status: str = "idle"
        self._last_error: Optional[str] = None
        self._current_match_id: Optional[str] = None

    # ------------------------------------------------------------------
    # 生命周期控制
    # ------------------------------------------------------------------

    def start(self, players: Optional[List[str]] = None) -> Dict[str, Any]:
        with self._lock:
            if self._game and self._game.is_running():
                raise RuntimeError("当前已有正在运行的对局")

            chosen_players = list(players) if players else list(self._players_template)
            if not chosen_players:
                raise ValueError("玩家列表不能为空")

            config = deepcopy(self._base_config)
            config['players'] = chosen_players

            self._game = GameLoop(config, state_store=self._state_store)
            self._game.initialize_game(chosen_players)
            self._current_match_id = self._game.match_id
            self._status = "running"
            self._last_error = None

            def _on_finish() -> None:
                with self._lock:
                    self._status = "finished"

            try:
                self._game.start_async(on_finish=_on_finish)
            except Exception as exc:  # noqa: BLE001
                self._status = "error"
                self._last_error = str(exc)
                logger.exception("启动游戏循环失败")
                raise

            return {"match_id": self._current_match_id}

    def pause(self) -> None:
        with self._lock:
            if not self._game or not self._game.is_running():
                raise RuntimeError("没有正在运行的对局可供暂停")
            if self._game.is_paused():
                return
            if self._game.pause():
                self._status = "paused"

    def resume(self) -> None:
        with self._lock:
            if not self._game or not self._game.is_running():
                raise RuntimeError("没有正在运行的对局可供继续")
            if self._game.is_paused() and self._game.resume():
                self._status = "running"

    def stop(self) -> None:
        with self._lock:
            if not self._game or not self._game.is_running():
                return
            if self._game.stop():
                self._status = "stopping"
        self._game.wait_for_completion()
        with self._lock:
            if self._status == "stopping":
                self._status = "stopped"

    # ------------------------------------------------------------------
    # 状态与保存
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            payload: Dict[str, Any] = {
                "state": self._status,
                "is_running": bool(self._game and self._game.is_running()),
                "is_paused": bool(self._game and self._game.is_paused()),
                "match_id": self._current_match_id,
            }
            if self._game:
                phase = self._game.phase_manager.current_phase
                payload["phase"] = getattr(phase, "name", None)
                payload["round"] = self._game.game_state.get("round_number")
            if self._last_error:
                payload["last_error"] = self._last_error
            return payload

    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        game = None
        with self._lock:
            game = self._game
        if game is not None:
            game.wait_for_completion(timeout=timeout)

    def save(self, filename: Optional[str] = None) -> Dict[str, Any]:
        if not self._state_store:
            raise RuntimeError("当前运行模式不支持保存对局")
        match = self._state_store.get_match()
        if not match:
            raise RuntimeError("暂无活跃对局可保存")

        match_id = match.get("match_id") or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = filename or f"{match_id}_{timestamp}.json"
        path = self._save_dir / name

        with path.open("w", encoding="utf-8") as fp:
            json.dump(match, fp, ensure_ascii=False, indent=2)

        logger.info(f"保存对局数据至 {path}")
        return {
            "filename": name,
            "path": str(path),
            "match_id": match_id,
        }

    def list_saves(self) -> List[Dict[str, Any]]:
        if not self._save_dir.exists():
            return []
        saves: List[Dict[str, Any]] = []
        for path in sorted(self._save_dir.glob("*.json")):
            stat = path.stat()
            saves.append(
                {
                    "filename": path.name,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size,
                }
            )
        return saves

    def load(self, filename: str, *, activate: bool = True) -> Dict[str, Any]:
        if not self._state_store:
            raise RuntimeError("当前运行模式不支持加载对局")
        path = self._save_dir / filename
        if not path.exists():
            raise FileNotFoundError(str(path))

        with path.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)

        activate_flag = bool(activate) and not (self._game and self._game.is_running())
        match_id = self._state_store.import_match(payload, activate=activate_flag)
        logger.info(f"从存档 {path} 加载对局 {match_id}")
        return {"match_id": match_id}
