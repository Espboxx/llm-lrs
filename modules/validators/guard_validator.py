from modules.validators.base_validator import BaseActionValidator
from modules.actions.base_actions import BaseNightAction

class GuardActionValidator(BaseActionValidator):
    @staticmethod
    def validate(action: BaseNightAction, game_state: dict) -> bool:
        from modules.roles.guard import Guard
        try:
            guard = game_state['players'][action.actor].role
            return (
                isinstance(guard, Guard) and
                action.target != guard.last_protected and
                action.target in game_state['alive_players'] and
                game_state['current_phase'] == PhaseManager.GamePhase.NIGHT
            )
        except KeyError as e:
            import logging
            logging.error(f"Guard validation error: {str(e)}")
            return False 