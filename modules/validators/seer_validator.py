from modules.actions.base_actions import BaseNightAction
from core.engine.phase_manager import PhaseManager
import logging

logger = logging.getLogger(__name__)

class SeerActionValidator:
    @staticmethod
    def validate(action: BaseNightAction, game_state: dict) -> bool:
        from modules.roles.seer import Seer  # 延迟导入
        try:
            config = game_state.get('config', {})
            allow_self = config.get('SEER_CONFIG', {}).get('allow_self_check', False)
            
            seer = game_state['players'][action.actor].role
            target_valid = (
                action.target in game_state['alive_players'] and 
                (allow_self or action.target != action.actor)
            )
            
            return (
                isinstance(seer, Seer) and
                seer.checks_remaining > 0 and
                target_valid and
                game_state['current_phase'] == PhaseManager.GamePhase.NIGHT and
                seer.cooldowns['check'] == 0
            )
        except KeyError as e:
            logger.error(f"Seer action validation error: {str(e)}")
            return False 