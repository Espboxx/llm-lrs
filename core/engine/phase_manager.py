from enum import Enum
from typing import List, Dict, Optional, Callable, Any
from functools import wraps
import logging
 
import time
from .victory_checker import VictoryChecker, Team

logger = logging.getLogger(__name__)

class GamePhase(Enum):
    """游戏阶段枚举"""
    WAITING = "waiting"          # 等待开始
    DAY_DISCUSSION = "day"       # 白天讨论
    DAY_VOTE = "vote"           # 白天投票
    NIGHT = "night"             # 夜晚行动
    GAME_OVER = "game_over"     # 游戏结束

class PhaseErrorLevel(Enum):
    """阶段错误等级"""
    WARNING = 1    # 可继续运行
    CRITICAL = 2   # 必须终止游戏

class PhaseHandler:
    """阶段处理器包装类"""
    def __init__(self, 
                 handler: Callable, 
                 priority: int = 0,
                 before_phase: Optional[Callable] = None,
                 after_phase: Optional[Callable] = None):
        self.handler = handler
        self.priority = priority
        self.before_phase = before_phase
        self.after_phase = after_phase
        
    def __call__(self, *args, **kwargs) -> Any:
        """调用处理器"""
        try:
            if self.before_phase:
                self.before_phase()
            result = self.handler(*args, **kwargs)
            if self.after_phase:
                self.after_phase()
            return result
        except Exception as e:
            logger.error(f"Handler execution failed: {str(e)}")
            raise

class PhaseManager:
    """游戏阶段管理器"""
    def __init__(self):
        self.current_phase: GamePhase = GamePhase.WAITING
        self.phase_handlers: Dict[GamePhase, List[PhaseHandler]] = {
            phase: [] for phase in GamePhase
        }
        self._dirty_flags = {phase: False for phase in GamePhase}
        self.phase_timeout: int = 300
        self._phase_callbacks: List[PhaseHandler] = []
        self.victory_checker = VictoryChecker()
        self._game_winner = None
        self.phase_timers: Dict[GamePhase, int] = {
            GamePhase.DAY_DISCUSSION: 600,
            GamePhase.DAY_VOTE: 300,
            GamePhase.NIGHT: 450,
            GamePhase.GAME_OVER: 0
        }
        self._phase_start_time = time.time()
        self._current_phase_timeout = self.phase_timeout
        
    def register_phase_handler(self, phase: GamePhase, priority: int = 0):
        """阶段处理器注册装饰器"""
        def decorator(handler: Callable):
            @wraps(handler)
            def wrapper(*args, **kwargs):
                try:
                    return handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Phase handler failed: {str(e)}")
                    raise
            
            self.phase_handlers[phase].append(
                PhaseHandler(wrapper, priority)
            )
            self._dirty_flags[phase] = True
            return wrapper
        return decorator
        
    def transition_to(self, new_phase: GamePhase):
        """转换游戏阶段"""
        try:
            if new_phase not in GamePhase:
                raise ValueError(f"Invalid game phase: {new_phase}")
                
            old_phase = self.current_phase
            self.current_phase = new_phase
            
            # 设置阶段超时
            self._current_phase_timeout = self.phase_timers.get(new_phase, self.phase_timeout)
            self._phase_start_time = time.time()
            
            logger.info(f"Phase changed from {old_phase.name} to {new_phase.name}")
            
            # 按需排序并执行处理器
            if self._dirty_flags[new_phase]:
                self.phase_handlers[new_phase].sort(key=lambda x: x.priority)
                self._dirty_flags[new_phase] = False
                
            for handler in self.phase_handlers[new_phase]:
                handler()
                
            # 触发回调
            for callback in self._phase_callbacks:
                callback(old_phase, new_phase)
                
        except Exception as e:
            logger.error(f"Phase transition failed: {str(e)}")
            self.current_phase = GamePhase.GAME_OVER
            
    def get_remaining_time(self) -> float:
        """获取当前阶段剩余时间"""
        if self.current_phase == GamePhase.GAME_OVER:
            return 0.0
        elapsed = time.time() - self._phase_start_time
        return max(self._current_phase_timeout - elapsed, 0.0)
    
    def start_game(self):
        """开始游戏"""
        if self.current_phase != GamePhase.WAITING:
            raise RuntimeError("Game has already started")
        logger.info("Game starting...")
        self.transition_to(GamePhase.NIGHT)
        
    def check_victory(self) -> bool:
        """检查是否有胜利者"""
        if winner := self.victory_checker.check_victory():
            self._game_winner = winner
            self.transition_to(GamePhase.GAME_OVER)
            return True
        return False

__all__ = ['PhaseManager', 'GamePhase'] 
