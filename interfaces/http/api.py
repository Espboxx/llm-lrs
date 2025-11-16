from __future__ import annotations

from pathlib import Path
from typing import Optional

from flask import Flask, abort, jsonify, send_from_directory, request

from services.game_state_store import GameStateStore


def create_app(
    state_store: GameStateStore,
    static_dir: Path,
    controller: Optional["GameController"] = None,
) -> Flask:
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

    @app.get("/api/game/status")
    def game_status():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        return jsonify(controller.get_status())

    @app.post("/api/game/start")
    def game_start():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        payload = request.get_json(silent=True) or {}
        players = payload.get("players")
        if players is not None and not isinstance(players, list):
            return jsonify({"error": "players 字段必须是数组"}), 400
        try:
            result = controller.start(players=players)
            return jsonify(result)
        except (RuntimeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/game/pause")
    def game_pause():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        try:
            controller.pause()
            return jsonify(controller.get_status())
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/game/resume")
    def game_resume():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        try:
            controller.resume()
            return jsonify(controller.get_status())
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/game/save")
    def game_save():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        payload = request.get_json(silent=True) or {}
        filename = payload.get("filename")
        try:
            result = controller.save(filename=filename)
            return jsonify(result)
        except (RuntimeError, FileNotFoundError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.get("/api/game/saves")
    def game_saves():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        return jsonify({"saves": controller.list_saves()})

    @app.post("/api/game/load")
    def game_load():
        if controller is None:
            return jsonify({"error": "游戏控制器未启用"}), 503
        payload = request.get_json(silent=True) or {}
        filename = payload.get("filename")
        if not filename:
            return jsonify({"error": "缺少 filename"}), 400
        activate = payload.get("activate", True)
        try:
            result = controller.load(filename, activate=bool(activate))
            return jsonify(result)
        except FileNotFoundError as exc:
            return jsonify({"error": f"存档不存在: {exc}"}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 400

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
    controller: Optional["GameController"] = None,
) -> None:
    """启动Flask应用，供后台线程调用。"""
    resolved_static = Path(static_dir or Path(__file__).resolve().parent / "static")
    app = create_app(state_store, resolved_static, controller)
    app.run(host=host, port=port, use_reloader=False)
