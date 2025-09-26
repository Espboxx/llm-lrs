from dotenv import load_dotenv
load_dotenv()

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

        self.client = self._build_client()
        self.model = os.getenv(
            "OPENAI_MODEL_NAME",
            os.getenv("AI_MODEL_NAME", "gpt-4-mini" if self.ai_provider == "openai" else "llama2")
        )

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
            content = self._extract_choice_content(response, context="action")
            if content is None:
                return {"target_id": None}

            decision = self._parse_response(content)
            return self._normalize_decision(decision, game_state)
        except Exception as e:
            logger.exception(f"AI决策出错: {str(e)}")
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
            content = self._extract_choice_content(response, context="speech")
            if content is None:
                return "我需要更多时间思考。"
            return content.split("</think>")[-1]
        except Exception as e:
            logger.exception(f"AI发言生成出错: {str(e)}")
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
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"target_id": None}
        except json.JSONDecodeError as decode_error:
            logger.error(f"AI响应JSON解析失败: {decode_error}; 原始内容: {response}")
        except Exception as unexpected:
            logger.exception(f"无法解析AI响应: {response}; 错误: {unexpected}")
            return {"target_id": None}
        return {"target_id": None}

    def _extract_choice_content(self, response: Any, context: str) -> Optional[str]:
        """提取补全内容，若缺失则记录日志"""
        choices = getattr(response, "choices", None) or []
        for choice in choices:
            message = getattr(choice, "message", None)
            content = getattr(message, "content", None)
            if content:
                return content

        logger.error(f"AI响应缺少内容，context={context}; response={response}")
        return None

    def _build_client(self) -> OpenAI:
        """根据提供商构建 OpenAI 客户端配置"""
        api_key = os.getenv("OPENAI_API_KEY") if self.ai_provider == "openai" else "not-needed"
        # openai 官方客户端在 base_url 为空时使用默认域名
        default_base_url = None if self.ai_provider == "openai" else "http://localhost:11434/v1"
        base_url = os.getenv("OPENAI_BASE_URL") or default_base_url

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        return OpenAI(**client_kwargs)

    def _normalize_decision(self, decision: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
        # 校验并规范化AI输出的目标
        normalized = dict(decision or {})
        target = normalized.get('target_id')
        players = game_state.get('players', {}) if isinstance(game_state, dict) else {}

        if isinstance(target, str):
            candidate = target.strip()
            lowered = candidate.lower()
            if lowered in {'', 'none', 'null', 'skip', 'pass', 'no', 'noone', 'no one', 'n/a'}:
                normalized['target_id'] = None
                return normalized

            lookup = {pid.lower(): pid for pid in players.keys()}
            if lowered in lookup:
                normalized['target_id'] = lookup[lowered]
            else:
                normalized['target_id'] = None
        else:
            normalized['target_id'] = None

        return normalized
