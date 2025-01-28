from typing import Dict, Any
from core.engine.phase_manager import GamePhase

class ConfigValidator:
    """配置验证器"""
    REQUIRED_KEYS = {
        'PHASE_CONFIG': {
            GamePhase.DAY_DISCUSSION,
            GamePhase.DAY_VOTE,
            GamePhase.NIGHT
        },
        'ROLE_DISTRIBUTION': dict,
        'ROLE_COOLDOWNS': dict,
        # 根据实际使用的角色保留配置项
        'SEER_CONFIG': dict,
        'WITCH_CONFIG': dict,
        'HUNTER_CONFIG': dict,
        'GUARD_CONFIG': dict
    }

    @staticmethod
    def validate(config: Dict[str, Any]) -> bool:
        """验证游戏配置是否合法
        
        Args:
            config: 游戏配置字典
            
        Returns:
            bool: 配置是否合法
            
        Raises:
            ValueError: 配置不合法时抛出，并说明原因
        """
        # 验证必需的配置项
        required_configs = [
            'PHASE_CONFIG',
            'ROLE_COOLDOWNS',
            'ROLE_DISTRIBUTION',
            'players'
        ]
        for config_name in required_configs:
            if config_name not in config:
                raise ValueError(f"缺少必需的配置项: {config_name}")
                
        # 验证玩家数量
        players = config['players']
        if not players:
            raise ValueError("玩家列表不能为空")
            
        # 验证角色分配
        role_dist = config['ROLE_DISTRIBUTION']
        total_roles = sum(role_dist.values())
        if total_roles != len(players):
            raise ValueError(
                f"角色数量({total_roles})与玩家数量({len(players)})不匹配"
            )
            
        # 验证阶段配置
        phase_config = config['PHASE_CONFIG']
        required_phases = [GamePhase.DAY_DISCUSSION, GamePhase.DAY_VOTE, GamePhase.NIGHT]
        for phase in required_phases:
            if phase not in phase_config:
                raise ValueError(f"缺少必需的游戏阶段配置: {phase.name}")
            phase_settings = phase_config[phase]
            if 'duration' not in phase_settings:
                raise ValueError(f"阶段 {phase.name} 缺少持续时间配置")
            if phase_settings['duration'] <= 0:
                raise ValueError(f"阶段 {phase.name} 的持续时间必须大于0")
                
        # 验证角色冷却时间
        cooldowns = config['ROLE_COOLDOWNS']
        for role, skills in cooldowns.items():
            for skill, cd in skills.items():
                if not isinstance(cd, (int, float)) or cd < 0:
                    raise ValueError(
                        f"角色 {role} 的技能 {skill} 冷却时间无效: {cd}"
                    )
                    
        # 验证特殊角色配置
        if 'SEER_CONFIG' in config:
            seer_config = config['SEER_CONFIG']
            if 'max_checks' in seer_config and seer_config['max_checks'] <= 0:
                raise ValueError("预言家最大查验次数必须大于0")
                
        if 'WITCH_CONFIG' in config:
            witch_config = config['WITCH_CONFIG']
            if 'can_save_self' not in witch_config:
                raise ValueError("女巫配置缺少can_save_self选项")
                
        if 'GUARD_CONFIG' in config:
            guard_config = config['GUARD_CONFIG']
            if 'max_protects' in guard_config and guard_config['max_protects'] <= 0:
                raise ValueError("守卫最大守护次数必须大于0")
                
        return True  # 所有检查通过 