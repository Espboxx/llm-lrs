from modules.validators.base_validator import BaseActionValidator
from modules.actions.base_actions import BaseDayAction

class ThiefActionValidator(BaseActionValidator):
    @staticmethod
    def validate(action: BaseDayAction, game_state: dict) -> bool:
        from modules.roles.thief import Thief
        try:
            thief = game_state['players'][action.actor].role
            return (
                isinstance(thief, Thief) and
                action.extra_data['selected_role'] in game_state['remaining_roles']
            )
        except KeyError as e:
            import logging
            logging.error(f"Thief validation error: {str(e)}")
            return False 