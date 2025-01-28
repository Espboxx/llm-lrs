from modules.validators.base_validator import BaseActionValidator
from modules.actions.base_actions import BaseNightAction

class WitchActionValidator(BaseActionValidator):
    @staticmethod
    def validate(action: BaseNightAction, game_state: dict) -> bool:
        from modules.roles.witch import Witch
        # 实现细节... 