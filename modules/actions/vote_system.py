from typing import Dict, List, Optional
from collections import defaultdict

class VoteManager:
    """投票管理器"""
    def __init__(self):
        self.votes: Dict[str, str] = {}  # 投票记录 {voter: target}
        self.vote_weights: Dict[str, float] = {}  # 投票权重
        self.vote_counts: Dict[str, int] = defaultdict(int)  # 得票统计
        self.abstain_votes = 0  # 弃权票数
        
    def reset(self):
        """重置投票状态"""
        self.votes.clear()
        self.vote_counts.clear()
        self.abstain_votes = 0
        
    def set_vote_weight(self, player_id: str, weight: float):
        """设置玩家投票权重"""
        self.vote_weights[player_id] = weight
        
    def cast_vote(self, voter: str, target: Optional[str] = None):
        """投票
        
        Args:
            voter: 投票者ID
            target: 投票目标ID，None表示弃权
        """
        if target is None:
            self.abstain_votes += 1
            return
            
        # 记录投票
        self.votes[voter] = target
        weight = self.vote_weights.get(voter, 1.0)
        self.vote_counts[target] += weight
        
    def get_vote_result(self) -> Dict[str, float]:
        """获取投票结果"""
        return dict(self.vote_counts)
        
    def resolve_votes(self) -> Optional[str]:
        """解析投票结果，返回被处决的玩家ID
        
        如果出现平票或无人投票，返回None
        """
        if not self.vote_counts:
            return None
            
        # 找出最高票数
        max_votes = max(self.vote_counts.values())
        # 获取最高票玩家列表
        top_voted = [
            player for player, votes in self.vote_counts.items()
            if votes == max_votes
        ]
        
        # 如果只有一个最高票，返回该玩家
        if len(top_voted) == 1:
            return top_voted[0]
        return None  # 平票或无人投票
        
    def get_voter_choice(self, voter: str) -> Optional[str]:
        """获取指定玩家的投票选择"""
        return self.votes.get(voter)
        
    def get_vote_summary(self) -> str:
        """获取投票摘要"""
        summary = []
        for voter, target in self.votes.items():
            weight = self.vote_weights.get(voter, 1.0)
            if weight != 1.0:
                summary.append(f"{voter}(权重{weight})投票给了{target}")
            else:
                summary.append(f"{voter}投票给了{target}")
        if self.abstain_votes:
            summary.append(f"有{self.abstain_votes}票弃权")
        return "\n".join(summary)
        
    def get_top_voted(self, n: int = 3) -> List[tuple]:
        """获取得票最多的n个玩家
        
        Returns:
            List of (player_id, vote_count) tuples
        """
        sorted_votes = sorted(
            self.vote_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_votes[:n]

class VoteValidator:
    """投票验证器"""
    @staticmethod
    def validate(voter_id: str, target_id: str, game_state: Dict) -> bool:
        """验证投票有效性"""
        return (
            voter_id in game_state['alive_players'] and
            target_id in game_state['alive_players'] and
            voter_id != target_id
        ) 