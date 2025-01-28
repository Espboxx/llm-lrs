from abc import ABC, abstractmethod
from modules.actions.base_actions import BaseNightAction, BaseDayAction

class BaseActionValidator(ABC):
    @staticmethod
    @abstractmethod
    def validate(action, game_state) -> bool:
        pass 