from typing import Dict, List
from modules.comms.message_router import MessageRouter

class AgentManager:
    """智能体管理系统"""
    def __init__(self, message_router: MessageRouter):
        self.agents: Dict[str, Agent] = {}
        self.router = message_router
        
    def register_agent(self, agent: 'Agent'):
        """注册智能体"""
        self.agents[agent.agent_id] = agent
        # 设置消息回调
        self.router.register_channel(agent.agent_id, agent.receive_message)
        
    def activate_agents(self):
        """激活所有智能体"""
        for agent in self.agents.values():
            agent.initialize()
            
class Agent:
    """智能体基类"""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.memory = []
        
    def initialize(self):
        """初始化智能体"""
        raise NotImplementedError
        
    def receive_message(self, message: dict):
        """接收消息"""
        self.memory.append(message)
        
    def send_message(self, content: str, channel: str):
        """发送消息"""
        raise NotImplementedError 