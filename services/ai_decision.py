from dotenv import load_dotenv
load_dotenv()

import openai
from openai import OpenAI
from typing import Dict, Any, Optional
from utils.logger import logger
import os

class AIDecisionService:
    """AI决策服务，使用OpenAI API来为玩家生成决策和发言"""
    
    def __init__(self):
        """初始化AI决策服务
        
        Args:
            api_key: OpenAI API密钥
        """
        # 从环境变量获取配置
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")  # 新增AI提供商配置
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY") if self.ai_provider == "openai" else "not-needed",
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")  # Ollama默认地址
        )
        self.model = os.getenv("AI_MODEL_NAME", "gpt-4-mini" if self.ai_provider == "openai" else "llama2")

    def get_player_action(self, player_id: str, role: str, game_state: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """获取玩家行动决策
        
        Args:
            player_id: 玩家ID
            role: 玩家角色
            game_state: 当前游戏状态
            phase: 当前游戏阶段
            
        Returns:
            Dict[str, Any]: 决策结果，包含target_id等信息
        """
        prompt = self._build_prompt(player_id, role, game_state, phase)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个狼人杀游戏中的AI玩家，需要根据当前游戏状态做出最优决策。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI决策出错: {str(e)}")
            return {"target_id": None}
            
    def get_player_speech(self, player_id: str, role: str, game_state: Dict[str, Any]) -> Optional[str]:
        """生成玩家发言
        
        Args:
            player_id: 玩家ID
            role: 玩家角色
            game_state: 当前游戏状态
            
        Returns:
            Optional[str]: 生成的发言内容
        """
        prompt = self._build_speech_prompt(player_id, role, game_state)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个狼人杀游戏中的AI玩家，需要根据当前游戏状态生成合适的发言。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            content = response.choices[0].message.content
            return content.split("</think>")[-1]
        except Exception as e:
            logger.error(f"AI发言生成出错: {str(e)}")
            return "我需要更多时间思考。"
            
    def _build_prompt(self, player_id: str, role: str, game_state: Dict[str, Any], phase: str) -> str:
        """构建决策提示
        
        Args:
            player_id: 玩家ID
            role: 玩家角色
            game_state: 当前游戏状态
            phase: 当前游戏阶段
            
        Returns:
            str: 构建的提示文本
        """
        alive_players = game_state['alive_players']
        dead_players = game_state['dead_players']
        round_number = game_state['round_number']
        
        prompt = f"""
        你是玩家 {player_id}，角色是 {role}。
        现在是第 {round_number} 轮的 {phase} 阶段。
        
        存活玩家: {', '.join(alive_players)}
        已死亡玩家: {', '.join(dead_players)}
        
        请根据当前游戏状态，选择一个目标玩家。
        回复文本格式: {{"target_id": "playerX"}}
        """
        return prompt
        
    def _build_speech_prompt(self, player_id: str, role: str, game_state: Dict[str, Any]) -> str:
        """构建发言提示
        
        Args:
            player_id: 玩家ID
            role: 玩家角色
            game_state: 当前游戏状态
            
        Returns:
            str: 构建的提示文本
        """
        alive_players = game_state['alive_players']
        dead_players = game_state['dead_players']
        round_number = game_state['round_number']
        speech_history = game_state.get('speech_history', [])
        
        # 构建发言历史文本
        speech_history_text = ""
        if speech_history:
            speech_history_text = "\n发言历史:\n"
            for speech in speech_history:
                speech_history_text += f"玩家{speech['player_id']}({speech['role']}): {speech['content']}\n"
        
        prompt = f"""
        你是玩家 {player_id}，角色是 {role}。
        现在是第 {round_number} 轮的讨论阶段。
        
        存活玩家: {', '.join(alive_players)}
        已死亡玩家: {', '.join(dead_players)}
        {speech_history_text}
        请根据你的角色和当前游戏状态，生成一段合适的发言。
        发言应该符合你的角色身份，并有助于你的阵营获胜。
        发言要考虑其他玩家的发言内容，做出合理的回应或质疑。
        """
        return prompt
        
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析API响应
        
        Args:
            response: API响应文本
            
        Returns:
            Dict[str, Any]: 解析后的决策结果
        """
        try:
            # 尝试解析JSON响应
            import json
            # 提取JSON部分
            import re
            content = response.split("</think>")[-1]
            json_match = re.search(r'\{.*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return {"target_id": None}
        except:
            # 如果解析失败，返回空结果
            logger.error(f"无法解析AI响应: {response}")
            return {"target_id": None} 