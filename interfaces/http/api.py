from __future__ import annotations

from pathlib import Path
from typing import Optional

from flask import Flask, abort, jsonify, send_from_directory

from services.game_state_store import GameStateStore


def create_app(state_store: GameStateStore, static_dir: Path) -> Flask:
    """构建用于观战的Flask应用。"""
    app = Flask(__name__, static_folder=str(static_dir), static_url_path="")

    @app.get("/api/matches")
    def list_matches():
        return jsonify({"matches": state_store.list_matches()})

    @app.get("/api/matches/<match_id>/speech-log")
    def speech_log(match_id: str):
        match = state_store.get_match(match_id)
        if match is None:
            abort(404)
        return jsonify(match)

    @app.get("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    return app


def run_app(
    state_store: GameStateStore,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    static_dir: Optional[Path] = None,
) -> None:
    """启动Flask应用，供后台线程调用。"""
    resolved_static = Path(static_dir or Path(__file__).resolve().parent / "static")
    app = create_app(state_store, resolved_static)
    app.run(host=host, port=port, use_reloader=False)
