import time
import random
from threading import Event, Lock, Thread
from typing import Dict, Any, List, Tuple, Optional, Callable
from core.engine.phase_manager import PhaseManager, GamePhase
from modules.roles.role_factory import RoleFactory
from modules.roles.cupid import Cupid
from core.engine.victory_checker import Team
from modules.roles.thief import Thief
from modules.comms.message_router import MessageRouter
from core.engine.config_validator import ConfigValidator
from modules.roles.base_role import BaseRole
from modules.roles.seer import Seer
from modules.roles.werewolf import Werewolf
from modules.roles.witch import Witch
from modules.roles.guard import Guard
from utils.logger import logger
from modules.actions.vote_system import VoteManager
from services.ai_decision import AIDecisionService
from services.game_state_store import GameStateStore

class GameLoop:
    """游戏核心循环"""
    def __init__(self, config: Dict[str, Any], state_store: Optional[GameStateStore] = None):
        ConfigValidator.validate(config)  # 验证配置
        self.phase_manager = PhaseManager()
        self.players: Dict[str, Player] = {}
        self.game_state = {
            'alive_players': [],
            'dead_players': [],
            'current_phase': None,
            'day_number': 0,
            'round_number': 1,  # 添加轮次计数
            'role_changes': {},
            'config': config,  # 添加配置到游戏状态
            'players': {},  # 添加玩家字典引用
            'speech_history': [],  # 添加发言历史记录
            'match_id': None,
        }
        self.pending_actions: List[Any] = []  # 待处理动作队列
        self.message_router = MessageRouter()
        self.config = config
        self.vote_manager = VoteManager()  # 添加投票管理器
        self.ai_service = AIDecisionService()  # 初始化AI服务
        self.state_store = state_store
        self.match_id: Optional[str] = None
        self._pause_event = Event()
        self._stop_event = Event()
        self._status_lock = Lock()
        self._thread: Optional[Thread] = None
        self._running = False
        self._paused = False
        self._on_finish: Optional[Callable[[], None]] = None
        self._pause_event.set()
        self._register_state_store_handlers()

    def start_async(self, *, on_finish: Optional[Callable[[], None]] = None) -> Thread:
        """以后台线程启动游戏循环。"""
        with self._status_lock:
            if self._thread and self._thread.is_alive():
                raise RuntimeError("Game loop is already running")
            self._stop_event.clear()
            self._pause_event.set()
            self._paused = False
            self._on_finish = on_finish
            self._thread = Thread(target=self._run_wrapper, daemon=True)
            self._thread.start()
            return self._thread

    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        thread = None
        with self._status_lock:
            thread = self._thread
        if thread is not None:
            thread.join(timeout=timeout)

    def pause(self) -> bool:
        with self._status_lock:
            if not self._running or self._paused:
                return False
            self._paused = True
            self._pause_event.clear()
            return True

    def resume(self) -> bool:
        with self._status_lock:
            if not self._running or not self._paused:
                return False
            self._paused = False
            self._pause_event.set()
            return True

    def stop(self) -> bool:
        with self._status_lock:
            if not self._running:
                return False
            self._stop_event.set()
            self._pause_event.set()
            return True

    def is_running(self) -> bool:
        with self._status_lock:
            return self._running

    def is_paused(self) -> bool:
        with self._status_lock:
            return self._paused

    def _run_wrapper(self) -> None:
        try:
            self.run()
        finally:
            callback = None
            with self._status_lock:
                callback = self._on_finish
                self._on_finish = None
                self._thread = None
            if callback:
                callback()

    def _prepare_for_run(self) -> None:
        with self._status_lock:
            self._stop_event.clear()
            self._pause_event.set()
            self._running = True
            self._paused = False

    def _finalize_run(self) -> None:
        with self._status_lock:
            self._running = False
            self._paused = False
            self._stop_event.set()

    def _sleep_with_control(self, duration: float) -> None:
        remaining = max(duration, 0)
        interval = 0.5
        while remaining > 0 and not self._stop_event.is_set():
            if not self._pause_event.wait(timeout=0.1):
                continue
            slice_len = min(interval, remaining)
            if self._stop_event.wait(slice_len):
                break
            remaining -= slice_len
        
    def _register_state_store_handlers(self) -> None:
        if not self.state_store:
            return
        # 将需要对观战面板透出的频道统一注册到状态存储处理器
        # 包含：系统消息、阶段变更、投票、指控、放逐
        for channel in ("system", "phase_change", "vote", "accuse", "exile"):
            self.message_router.register_handler(
                channel,
                lambda message, ch=channel: self._handle_router_message(ch, message),
            )

    def _handle_router_message(self, channel: str, message: Dict[str, Any]) -> None:
        if not self.state_store:
            return
        metadata = message.get("metadata") or {}
        if "round" in metadata and metadata["round"] is not None:
            round_number = metadata["round"]
        else:
            round_number = self.game_state.get("round_number")
        phase = metadata.get("phase")
        if phase is None:
            current_phase = self.game_state.get("current_phase")
            if current_phase is not None:
                phase = getattr(current_phase, "name", str(current_phase))
        content = message.get("content", "")
        metadata_to_store = metadata if metadata else None
        self.state_store.record_system_event(
            content=content,
            channel=channel,
            round_number=round_number,
            phase=phase,
            metadata=metadata_to_store,
        )

    def initialize_game(self, players: list):
        """初始化游戏"""
        # 记录游戏开始
        logger.info("游戏初始化开始")
        
        # 初始化玩家列表
        self.game_state['alive_players'] = players.copy()
        
        # 分配角色
        for player_id in players:
            role_name = self._assign_role(player_id)
            # 传递config参数
            role = RoleFactory.create_role(role_name, player_id, self.config)
            role.set_game_state(self.game_state)  # 设置游戏状态
            self.players[player_id] = Player(player_id, role)
            logger.role_reveal(player_id, role_name)
            
        # 更新游戏状态中的玩家引用
        self.game_state['players'] = self.players

        if self.state_store:
            self.match_id = self.state_store.start_match(players)
            self.game_state['match_id'] = self.match_id
            self._sync_store_players()
            
        # 注册到胜利检查器
        for player in self.players.values():
            self.phase_manager.victory_checker.register_player(
                player.id, player.role.team
            )
            
        # 处理丘比特匹配阶段
        cupids = [p for p in self.players.values() if isinstance(p.role, Cupid)]
        for cupid in cupids:
            # 获取丘比特选择的情侣
            lovers = self._get_cupid_selection(cupid.id)
            if lovers:
                self._process_lovers(lovers)
                logger.game_event("CUPID", f"玩家{lovers[0]}和{lovers[1]}成为情侣")
            
        # 处理盗贼角色分配
        thieves = [p for p in self.players.values() if isinstance(p.role, Thief)]
        for thief in thieves:
            self._process_thief_stealing()
            
        # 发送游戏开始通知
        start_msg = "游戏开始！分配的角色如下：\n"
        for player_id, player in self.players.items():
            start_msg += f"玩家 {player_id}: {type(player.role).__name__}\n"
        self.message_router.broadcast(
            start_msg.strip(),
            channel="system",
            recipients=self.game_state['alive_players'],
            metadata={
                "phase": "系统公告",
                "round": self.game_state['round_number'],
            },
        )
        logger.info("游戏初始化完成")
        
    def _process_lovers(self, lovers: Tuple[str, str]):
        """处理情侣关系"""
        for player_id in lovers:
            player = self.players[player_id]
            player.team = Team.LOVERS
            # 通知胜利检查器更新阵营
            self.phase_manager.victory_checker.register_player(player_id, Team.LOVERS)

    def run(self):
        """启动游戏循环"""
        self._prepare_for_run()
        logger.info("游戏循环开始")
        self.phase_manager.start_game()

        try:
            while (
                not self._stop_event.is_set()
                and self.phase_manager.current_phase != GamePhase.GAME_OVER
            ):
                if not self._pause_event.wait(timeout=0.1):
                    continue
                if self._stop_event.is_set():
                    break

                current_phase = self.phase_manager.current_phase
                self.game_state['current_phase'] = current_phase

                if self.state_store:
                    self.state_store.set_phase(
                        getattr(current_phase, "name", str(current_phase)),
                        self.game_state['round_number']
                    )
            
                # 更新所有存活角色的技能冷却
                for player_id in self.game_state['alive_players']:
                    player = self.players[player_id]
                    if isinstance(player.role, BaseRole):
                        player.role.update_cooldowns(current_phase)

                # 发送阶段开始通知
                phase_info = self.config['PHASE_CONFIG'].get(
                    current_phase,
                    {'description': '未知阶段', 'duration': 5}  # 默认5秒
                )

                # 显示轮次和阶段信息
                if current_phase == GamePhase.NIGHT:
                    logger.info(f"=== 第 {self.game_state['round_number']} 轮游戏开始 ===")
                    logger.info(f"存活玩家: {', '.join(self.game_state['alive_players'])}")

                notification = f"进入{phase_info['description']}，持续{phase_info['duration']}秒"
                self.message_router.broadcast(
                    notification,
                    channel="phase_change",
                    recipients=self.game_state['alive_players'],
                    metadata={
                        "phase": phase_info.get('description'),
                        "round": self.game_state['round_number'],
                    },
                )

                # 处理当前阶段
                if current_phase == GamePhase.NIGHT:
                    self._handle_night_phase()
                elif current_phase == GamePhase.DAY_DISCUSSION:
                    self._handle_discussion_phase()
                elif current_phase == GamePhase.DAY_VOTE:
                    self._handle_vote_phase()
                    # 只在投票阶段结束时增加轮次
                    next_phase = self._get_next_phase(current_phase)
                    if next_phase == GamePhase.NIGHT:
                        self.game_state['round_number'] += 1

                if self._stop_event.is_set():
                    break

                # 检查游戏是否结束
                if self.phase_manager.check_victory():
                    winner = self.phase_manager.victory_checker.get_winner()
                    logger.info(f"游戏结束！胜利阵营：{winner}")
                    logger.info(f"存活玩家: {', '.join(self.game_state['alive_players'])}")
                    break

                # 检查是否需要继续等待
                if len(self.game_state['alive_players']) <= 0:
                    logger.info("所有玩家已死亡，游戏结束")
                    break

                # 等待阶段时间
                if phase_info['duration'] > 0:
                    self._sleep_with_control(phase_info['duration'])
                    if self._stop_event.is_set():
                        break

                # 转换到下一个阶段
                next_phase = self._get_next_phase(current_phase)
                self.phase_manager.transition_to(next_phase)

                # 清理阶段状态
                if current_phase == GamePhase.NIGHT:
                    self.game_state['night_deaths'] = set()
                elif current_phase == GamePhase.DAY_VOTE:
                    self.game_state['day_deaths'] = set()
        finally:
            self._finalize_run()
            logger.info(f"=== 游戏在第 {self.game_state['round_number']} 轮结束 ===")
            logger.info("游戏循环结束")
        
    def _get_next_phase(self, current_phase: GamePhase) -> GamePhase:
        """获取下一个游戏阶段"""
        if current_phase == GamePhase.NIGHT:
            return GamePhase.DAY_DISCUSSION
        elif current_phase == GamePhase.DAY_DISCUSSION:
            return GamePhase.DAY_VOTE
        elif current_phase == GamePhase.DAY_VOTE:
            return GamePhase.NIGHT
        return GamePhase.GAME_OVER

    def _handle_night_phase(self):
        """处理夜晚阶段"""
        logger.info("=== 夜晚降临，天黑请闭眼 ===")
        
        # 初始化夜晚死亡列表
        self.game_state['night_deaths'] = set()
        
        # 狼人行动
        werewolves = [p for p in self.game_state['alive_players'] if isinstance(self.players[p].role, Werewolf)]
        if werewolves:
            logger.info("=== 狼人请睁眼，选择你要击杀的目标 ===")
            # 让每个狼人选择目标
            targets = {}
            for wolf_id in werewolves:
                decision = self.ai_service.get_player_action(
                    wolf_id,
                    'werewolf',
                    self.game_state,
                    'NIGHT'
                )
                target_id = decision.get('target_id')
                if target_id:
                    targets[wolf_id] = target_id
            logger.info("=== 狼人请闭眼 ===")
            
            # 统计投票结果
            if targets:
                from collections import Counter
                vote_count = Counter(targets.values())
                # 获取票数最多的目标
                target_id = max(vote_count.items(), key=lambda x: x[1])[0]
                if not any(isinstance(self.players[p].role, Guard) and 
                          self.players[p].role.last_protected == target_id 
                          for p in self.game_state['alive_players']):
                    self.game_state['night_deaths'].add(target_id)
                    logger.info(f"狼人选择了 {target_id}")
        
        # 女巫行动
        witches = [p for p in self.game_state['alive_players'] if isinstance(self.players[p].role, Witch)]
        for witch_id in witches:
            logger.info("=== 女巫请睁眼 ===")
            witch = self.players[witch_id].role
            
            # 如果有解药且有人死亡
            if witch.has_heal_potion and self.game_state['night_deaths']:
                logger.info(f"今晚 {', '.join(self.game_state['night_deaths'])} 死亡，是否使用解药？")
                decision = self.ai_service.get_player_action(
                    witch_id,
                    'witch',
                    {**self.game_state, 'action': 'heal'},
                    'NIGHT'
                )
                if decision.get('target_id') in self.game_state['night_deaths']:
                    self.game_state['night_deaths'].remove(decision['target_id'])
                    witch.has_heal_potion = False
                    logger.info("女巫使用了解药")
            
            # 如果有毒药
            if witch.has_poison_potion:
                logger.info("是否使用毒药？")
                decision = self.ai_service.get_player_action(
                    witch_id,
                    'witch',
                    {**self.game_state, 'action': 'poison'},
                    'NIGHT'
                )
                target_id = decision.get('target_id')
                if target_id and target_id not in self.game_state['night_deaths']:
                    self.game_state['night_deaths'].add(target_id)
                    witch.has_poison_potion = False
                    logger.info("女巫使用了毒药")
            logger.info("=== 女巫请闭眼 ===")
        
        # 守卫行动
        guards = [p for p in self.game_state['alive_players'] if isinstance(self.players[p].role, Guard)]
        for guard_id in guards:
            logger.info("=== 守卫请睁眼，选择要守护的对象 ===")
            decision = self.ai_service.get_player_action(
                guard_id,
                'guard',
                self.game_state,
                'NIGHT'
            )
            target_id = decision.get('target_id')
            if target_id:
                guard = self.players[guard_id].role
                # 如果目标在死亡名单中，将其移除
                if target_id in self.game_state['night_deaths']:
                    self.game_state['night_deaths'].discard(target_id)
                    logger.info("守卫成功保护了目标")
                guard.last_protected = target_id
            logger.info("=== 守卫请闭眼 ===")
        
        # 预言家行动
        seers = [p for p in self.game_state['alive_players'] if isinstance(self.players[p].role, Seer)]
        for seer_id in seers:
            logger.info("=== 预言家请睁眼，选择要查验的对象 ===")
            target_id = self._get_seer_target(seer_id)
            if target_id:
                # 使用check方法而不是直接设置结果
                self.players[seer_id].role.check(target_id, self.game_state)
                logger.info(f"预言家查验了 {target_id}")
            logger.info("=== 预言家请闭眼 ===")
        
        # 处理死亡
        if self.game_state['night_deaths']:
            logger.info(f"昨晚死亡的玩家是: {', '.join(self.game_state['night_deaths'])}")
            for dead_player in self.game_state['night_deaths']:
                self._kill_player(dead_player, "在夜晚死亡")
            
        logger.info("=== 天亮了 ===")
        # 显示存活玩家
        logger.info(f"存活玩家: {', '.join(self.game_state['alive_players'])}")
        
    def _process_deaths(self):
        """处理死亡玩家"""
        night_deaths = self.game_state.get('night_deaths', set())
        day_deaths = self.game_state.get('day_deaths', set())
        
        for player_id in night_deaths:
            if player_id in self.players:
                death_reason = "被狼人杀害"
                if player_id in self.game_state.get('witch_poison_targets', set()):
                    death_reason = "被女巫毒死"
                logger.death_event(player_id, death_reason)
                # 调用角色特定的死亡处理
                if hasattr(self.players[player_id].role, 'handle_death'):
                    self.players[player_id].role.handle_death(self)
                # 从存活列表移除
                if player_id in self.game_state['alive_players']:
                    self.game_state['alive_players'].remove(player_id)
                    self.game_state['dead_players'].append(player_id)
                # 通知胜利检查器
                self.phase_manager.victory_checker.remove_player(player_id)
                
        for player_id in day_deaths:
            if player_id in self.players:
                logger.death_event(player_id, "被投票处决")
                # 调用角色特定的死亡处理
                if hasattr(self.players[player_id].role, 'handle_death'):
                    self.players[player_id].role.handle_death(self)
                # 从存活列表移除
                if player_id in self.game_state['alive_players']:
                    self.game_state['alive_players'].remove(player_id)
                    self.game_state['dead_players'].append(player_id)
                # 通知胜利检查器
                self.phase_manager.victory_checker.remove_player(player_id)
                
        # 处理猎人等角色的延迟动作
        while self.pending_actions:
            action = self.pending_actions.pop(0)
            action.execute(self.game_state)
            logger.game_event("DELAYED_ACTION", str(action))

        self._sync_store_players()

    def _process_thief_stealing(self):
        """处理盗贼偷换角色"""
        thieves = [p for p in self.players.values() if isinstance(p.role, Thief)]
        for thief in thieves:
            available_roles = self._get_stealable_roles()
            # 获取盗贼选择
            action = self._get_thief_action(thief.id, available_roles)
            if action and action.validate(self.game_state):
                self._reassign_role(thief.id, action.extra_data['selected_role'])
                logger.game_event(
                    "THIEF",
                    f"盗贼{thief.id}选择了角色{action.extra_data['selected_role']}"
                )
            
    def _sync_store_players(self) -> None:
        """同步状态存储中的玩家列表。"""
        if self.state_store:
            self.state_store.update_players(
                self.game_state['alive_players'],
                self.game_state['dead_players']
            )

    def _get_stealable_roles(self) -> list:
        """获取可偷换角色"""
        return self.config.get(
            'THIEF_CONFIG', {}
        ).get('stealable_roles', ['werewolf', 'villager'])

    def _handle_thief_timeout(self):
        """处理盗贼超时未选择"""
        thieves = [p for p in self.players.values() if isinstance(p.role, Thief)]
        for thief in thieves:
            if self.config.get('THIEF_CONFIG', {}).get('must_steal', True):
                available_roles = self._get_stealable_roles()
                if available_roles:
                    # 随机选择一个可用角色
                    new_role = random.choice(available_roles)
                    self._reassign_role(thief.id, new_role)
                    logger.game_event(
                        "THIEF_TIMEOUT",
                        f"盗贼{thief.id}超时，随机分配角色{new_role}"
                    )

    def _reassign_role(self, player_id: str, new_role: str):
        """重新分配角色"""
        old_role = self.players[player_id].role
        # 先移除旧阵营信息
        self.phase_manager.victory_checker.remove_player(player_id)
        # 创建新角色并注册
        self.players[player_id].role = RoleFactory.create_role(new_role, player_id, self.config)
        self.phase_manager.victory_checker.register_player(
            player_id, 
            self.players[player_id].role.team
        )
        # 记录角色变更
        self.game_state['role_changes'][player_id] = new_role
        # 发送角色更换通知
        self.message_router.broadcast(
            f"玩家 {player_id} 更换角色为 {new_role}",
            channel="system",
            recipients=self.game_state['alive_players']
        )
        logger.role_reveal(player_id, new_role)

    def _handle_discussion_phase(self):
        """处理讨论阶段"""
        logger.info("进入讨论阶段")
        
        # 清空当前轮次的发言历史
        self.game_state['speech_history'] = []
        
        # 让每个存活的玩家发言
        for player_id in self.game_state['alive_players']:
            speech = self.ai_service.get_player_speech(
                player_id,
                type(self.players[player_id].role).__name__.lower(),
                self.game_state
            )
            if speech:
                # 记录发言
                self.game_state['speech_history'].append({
                    'player_id': player_id,
                    'role': type(self.players[player_id].role).__name__.lower(),
                    'content': speech,
                    'round': self.game_state['round_number']
                })
                if self.state_store:
                    self.state_store.record_speech(
                        player_id=player_id,
                        role=type(self.players[player_id].role).__name__.lower(),
                        content=speech,
                        round_number=self.game_state['round_number'],
                        phase=getattr(
                            self.game_state['current_phase'],
                            "name",
                            str(self.game_state['current_phase'])
                        ),
                    )
                logger.info(f"{player_id} 说: {speech}")

        logger.info("讨论阶段结束，准备进入投票阶段")
        
    def _handle_vote_phase(self):
        """处理投票阶段"""
        logger.info("=== 投票阶段开始 ===")
        
        # 初始化投票系统
        self.vote_manager.reset()
        self.game_state['day_deaths'] = set()
        
        # 收集所有玩家的投票
        for voter_id in self.game_state['alive_players']:
            target_id = self._get_vote_target(voter_id)
            if target_id:
                self.vote_manager.cast_vote(voter_id, target_id)
                logger.info(f"{voter_id} 投票给了 {target_id}")
                # 向观战面板记录结构化的投票事件
                try:
                    self.message_router.broadcast(
                        f"{voter_id} 投票给了 {target_id}",
                        channel="vote",
                        recipients=self.game_state['alive_players'],
                        metadata={
                            "from": voter_id,
                            "to": target_id,
                            "round": self.game_state['round_number'],
                            "phase": getattr(
                                self.game_state['current_phase'],
                                "name",
                                str(self.game_state['current_phase'])
                            ),
                        },
                    )
                except Exception:
                    # 记录失败不影响游戏流程
                    pass
            else:
                logger.info(f"{voter_id} 选择弃票")
        
        # 显示投票统计
        vote_summary = self.vote_manager.get_vote_summary()
        logger.info("=== 投票结果统计 ===")
        logger.info(vote_summary)
        
        # 处理投票结果
        vote_result = self.vote_manager.resolve_votes()
        if vote_result:
            logger.info(f"{vote_result} 被投票处决")
            self._execute_player(vote_result)
            # 向观战面板记录放逐事件（用于时间轴视觉强化）
            try:
                self.message_router.broadcast(
                    f"{vote_result} 被投票处决",
                    channel="exile",
                    recipients=self.game_state['alive_players'],
                    metadata={
                        "target": vote_result,
                        "round": self.game_state['round_number'],
                        "phase": getattr(
                            self.game_state['current_phase'],
                            "name",
                            str(self.game_state['current_phase'])
                        ),
                    },
                )
            except Exception:
                pass
        else:
            logger.info("投票未达成一致，没有人被处决")
        
        logger.info("=== 投票阶段结束 ===")

    def _get_seer_target(self, seer_id: str) -> Optional[str]:  
        """获取预言家的查验目标"""
        decision = self.ai_service.get_player_action(
            seer_id,
            'seer',
            self.game_state,
            GamePhase.NIGHT
        )
        return decision.get('target_id')

    def _get_vote_target(self, voter_id: str) -> str:
        """获取投票目标"""
        decision = self.ai_service.get_player_action(
            voter_id,
            self.players[voter_id].role.__class__.__name__.lower(),
            self.game_state,
            GamePhase.DAY_VOTE
        )
        return decision.get('target_id')

    def _execute_player(self, player_id: str):
        """处决玩家"""
        if player_id in self.game_state['alive_players']:
            self.game_state.setdefault('day_deaths', set()).add(player_id)
            self._kill_player(player_id, "被投票处决")

    def admin_override(self, command: str):
        """管理员命令覆写"""
        if command.startswith("SET_COOLDOWN"):
            # 示例命令：SET_COOLDOWN player1 kill 3
            _, player_id, skill, value = command.split()
            if player_id in self.players:
                player = self.players[player_id]
                if isinstance(player.role, BaseRole):
                    player.role.cooldowns[skill] = int(value)
                    logger.info(f"管理员设置{player_id}的{skill}冷却为{value}")
                    
    def _initialize_roles(self):
        """初始化角色分配"""
        role_dist = self.config['ROLE_DISTRIBUTION']
        available_roles = []
        for role, count in role_dist.items():
            available_roles.extend([role] * count)
        random.shuffle(available_roles)
        return available_roles
        
    def _assign_role(self, player_id: str) -> str:
        """为玩家分配角色"""
        if not hasattr(self, '_available_roles'):
            self._available_roles = self._initialize_roles()
        return self._available_roles.pop()

    def _kill_player(self, player_id: str, reason: str):
        """处理玩家死亡
        
        Args:
            player_id: 死亡玩家ID
            reason: 死亡原因
        """
        if player_id in self.game_state['alive_players']:
            # 从存活列表移除
            self.game_state['alive_players'].remove(player_id)
            # 添加到死亡列表
            self.game_state['dead_players'].append(player_id)
            # 通知胜利检查器
            self.phase_manager.victory_checker.remove_player(player_id)
            # 记录死亡事件
            logger.info(f"玩家 {player_id} {reason}")
            # 广播死亡消息
            self.message_router.broadcast(
                f"玩家 {player_id} {reason}",
                channel="system",
                recipients=self.game_state['alive_players']
            )
            # 调用角色的死亡处理方法（如果有）
            player = self.players[player_id]
            if hasattr(player.role, 'handle_death'):
                player.role.handle_death(self)

        self._sync_store_players()

class Player:
    """玩家类"""
    def __init__(self, player_id: str, role):
        self.id = player_id
        self.role = role
        self.team = role.team  # 初始团队与角色团队相同
        self.night_actions = []
        self.day_actions = []
        self.status = {
            'alive': True,
            'protected': False,
            'poisoned': False,
            'silenced': False
        }
        self.vote_power = 1  # 投票权重
        
    def add_night_action(self, action):
        """添加夜晚行动"""
        self.night_actions.append(action)
        
    def add_day_action(self, action):
        """添加白天行动"""
        self.day_actions.append(action)
        
    def reset_actions(self):
        """重置行动"""
        self.night_actions.clear()
        self.day_actions.clear()
        
    def is_alive(self) -> bool:
        """检查玩家是否存活"""
        return self.status['alive']
        
    def kill(self):
        """处理玩家死亡"""
        self.status['alive'] = False
        
    def protect(self):
        """守护玩家"""
        self.status['protected'] = True
        
    def unprotect(self):
        """移除守护状态"""
        self.status['protected'] = False
        
    def poison(self):
        """毒杀玩家"""
        self.status['poisoned'] = True
        
    def silence(self):
        """沉默玩家"""
        self.status['silenced'] = True
        
    def unsilence(self):
        """解除沉默"""
        self.status['silenced'] = False 
