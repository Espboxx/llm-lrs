from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utc_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class GameStateStore:
    """线程安全的游戏状态存储，用于对外提供观战数据。"""

    def __init__(self) -> None:
        self._lock = Lock()
        self._matches: Dict[str, Dict[str, Any]] = {}
        self._active_match_id: Optional[str] = None

    @property
    def active_match_id(self) -> Optional[str]:
        with self._lock:
            return self._active_match_id

    def start_match(self, players: List[str]) -> str:
        """初始化一局新的对局并返回match_id。"""
        match_id = uuid4().hex
        with self._lock:
            self._active_match_id = match_id
            self._matches[match_id] = {
                "created_at": _utc_iso(),
                "players": list(players),
                "alive_players": list(players),
                "dead_players": [],
                "phase": None,
                "round": 1,
                "speech_log": [],
            }
        return match_id

    def set_phase(self, phase: str, round_number: int) -> None:
        """记录当前阶段与轮次。"""
        with self._lock:
            match = self._get_active_match()
            if match is None:
                return
            match["phase"] = phase
            match["round"] = round_number

    def update_players(self, alive_players: List[str], dead_players: List[str]) -> None:
        """同步存活与死亡玩家列表。"""
        with self._lock:
            match = self._get_active_match()
            if match is None:
                return
            match["alive_players"] = list(alive_players)
            match["dead_players"] = list(dead_players)

    def record_speech(
        self,
        *,
        player_id: str,
        role: str,
        content: str,
        round_number: int,
        phase: str,
    ) -> None:
        """追加一条玩家发言记录。"""
        with self._lock:
            match = self._get_active_match()
            if match is None:
                return
            match["speech_log"].append(
                {
                    "player_id": player_id,
                    "role": role,
                    "content": content,
                    "round": round_number,
                    "phase": phase,
                    "timestamp": _utc_iso(),
                }
            )

    def list_matches(self) -> List[Dict[str, Any]]:
        """返回可供观战的对局概要列表。"""
        with self._lock:
            results = []
            for match_id, payload in self._matches.items():
                results.append(
                    {
                        "match_id": match_id,
                        "created_at": payload.get("created_at"),
                        "round": payload.get("round"),
                        "phase": payload.get("phase"),
                        "alive_players": list(payload.get("alive_players", [])),
                    }
                )
            return results

    def get_match(self, match_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取指定对局的详细信息。"""
        with self._lock:
            resolved_id = match_id or self._active_match_id
            if resolved_id is None:
                return None
            payload = self._matches.get(resolved_id)
            if payload is None:
                return None
            result = deepcopy(payload)
            result["match_id"] = resolved_id
            return result

    def _get_active_match(self) -> Optional[Dict[str, Any]]:
        if self._active_match_id is None:
            return None
        return self._matches.get(self._active_match_id)
