from typing import Dict, Any, List, Optional, Set, Callable
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class MessageRouter:
    """消息路由器"""
    
    def __init__(self):
        self.channels: Dict[str, Set[str]] = defaultdict(set)  # 频道订阅者
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)  # 消息处理器
        self.message_history: List[Dict[str, Any]] = []  # 消息历史
        self.max_history = 1000  # 最大历史消息数
        
    def subscribe(self, channel: str, subscriber: str):
        """订阅频道
        
        Args:
            channel: 频道名称
            subscriber: 订阅者ID
        """
        self.channels[channel].add(subscriber)
        
    def unsubscribe(self, channel: str, subscriber: str):
        """取消订阅频道
        
        Args:
            channel: 频道名称
            subscriber: 订阅者ID
        """
        if subscriber in self.channels[channel]:
            self.channels[channel].remove(subscriber)
            
    def register_handler(self, channel: str, handler: Callable):
        """注册消息处理器
        
        Args:
            channel: 频道名称
            handler: 处理器函数
        """
        self.handlers[channel].append(handler)
        
    def broadcast(self, message: str, channel: str = "system",
                 recipients: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """广播消息
        
        Args:
            message: 消息内容
            channel: 频道名称
            recipients: 指定接收者列表（可选）
            metadata: 消息元数据（可选）
        """
        # 构造消息对象
        msg_obj = {
            'content': message,
            'channel': channel,
            'recipients': recipients or list(self.channels[channel]),
            'metadata': metadata or {}
        }
        
        # 记录消息
        self._record_message(msg_obj)
        
        # 调用处理器
        for handler in self.handlers[channel]:
            try:
                handler(msg_obj)
            except Exception as e:
                logger.error(f"消息处理器异常: {str(e)}")
                
        # 记录日志
        logger.info(f"[{channel}] {message}")
        
    def send_private(self, message: str, recipient: str,
                    metadata: Optional[Dict[str, Any]] = None):
        """发送私聊消息
        
        Args:
            message: 消息内容
            recipient: 接收者ID
            metadata: 消息元数据（可选）
        """
        self.broadcast(
            message,
            channel="private",
            recipients=[recipient],
            metadata=metadata
        )
        
    def send_team(self, message: str, team: str,
                  recipients: List[str],
                  metadata: Optional[Dict[str, Any]] = None):
        """发送阵营消息
        
        Args:
            message: 消息内容
            team: 阵营名称
            recipients: 接收者列表
            metadata: 消息元数据（可选）
        """
        self.broadcast(
            message,
            channel=f"team_{team}",
            recipients=recipients,
            metadata=metadata
        )
        
    def _record_message(self, message: Dict[str, Any]):
        """记录消息
        
        Args:
            message: 消息对象
        """
        self.message_history.append(message)
        # 保持历史消息数量限制
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
            
    def get_history(self, channel: Optional[str] = None,
                   recipient: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """获取历史消息
        
        Args:
            channel: 频道名称过滤（可选）
            recipient: 接收者ID过滤（可选）
            limit: 返回消息数量限制
            
        Returns:
            List[Dict[str, Any]]: 历史消息列表
        """
        messages = self.message_history
        
        # 按频道过滤
        if channel:
            messages = [
                msg for msg in messages
                if msg['channel'] == channel
            ]
            
        # 按接收者过滤
        if recipient:
            messages = [
                msg for msg in messages
                if recipient in msg['recipients']
            ]
            
        return messages[-limit:]
        
    def clear_history(self):
        """清空历史消息"""
        self.message_history.clear()
        
    def get_channel_subscribers(self, channel: str) -> Set[str]:
        """获取频道订阅者
        
        Args:
            channel: 频道名称
            
        Returns:
            Set[str]: 订阅者ID集合
        """
        return self.channels[channel].copy() 