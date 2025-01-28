import logging
import os
from datetime import datetime

class GameLogger:
    """游戏日志记录器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 创建日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"game_{timestamp}.log")
        
        # 配置日志记录器
        self.logger = logging.getLogger("werewolf")
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
        
    def game_event(self, event_type: str, details: str):
        """记录游戏事件
        
        Args:
            event_type: 事件类型
            details: 事件详情
        """
        self.info(f"[{event_type}] {details}")
        
    def player_action(self, player_id: str, action: str, target: str = None):
        """记录玩家行动
        
        Args:
            player_id: 玩家ID
            action: 行动类型
            target: 目标玩家ID（可选）
        """
        if target:
            self.info(f"玩家{player_id}对{target}使用了{action}")
        else:
            self.info(f"玩家{player_id}执行了{action}")
            
    def phase_change(self, old_phase: str, new_phase: str):
        """记录阶段变更
        
        Args:
            old_phase: 旧阶段
            new_phase: 新阶段
        """
        self.info(f"游戏阶段从{old_phase}变更为{new_phase}")
        
    def death_event(self, player_id: str, cause: str):
        """记录玩家死亡
        
        Args:
            player_id: 死亡玩家ID
            cause: 死亡原因
        """
        self.info(f"玩家{player_id}死亡，原因：{cause}")
        
    def role_reveal(self, player_id: str, role: str):
        """记录角色身份揭示
        
        Args:
            player_id: 玩家ID
            role: 角色名称
        """
        self.info(f"玩家{player_id}的身份是{role}")
        
    def vote_record(self, voter: str, target: str):
        """记录投票信息
        
        Args:
            voter: 投票者ID
            target: 投票目标ID
        """
        self.info(f"玩家{voter}投票给了{target}")
        
    def game_over(self, winner: str, details: str = None):
        """记录游戏结束
        
        Args:
            winner: 获胜方
            details: 获胜详情（可选）
        """
        msg = f"游戏结束，{winner}获胜"
        if details:
            msg += f"：{details}"
        self.info(msg)

# 创建全局日志记录器实例
logger = GameLogger() 