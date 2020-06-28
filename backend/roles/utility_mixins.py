from ..resolver import GameAction, ActionMixin
from ..model import GameStage

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import WurwolvesGame


class OncePerGame(GameAction):
    @classmethod
    def is_action_available(
        cls, game: "WurwolvesGame", stage: GameStage, stage_id: int, player_id: int
    ):
        """
        Disallow the action if it's already been done this game
        """
        previous_actions = game.get_actions_model(
            player_id=player_id, stage=GameStage.NIGHT
        )

        return not bool(previous_actions)


class TargetRequired(ActionMixin):
    def __init__(self, action_model, players):
        if not action_model.selected_player_id:
            raise ValueError(f"{self.__class__} requires a target")
        super().__init__(action_model, players)


class NoTargetRequired(ActionMixin):
    def __init__(self, action_model, players):
        if action_model.selected_player_id:
            raise ValueError(f"{self.__class__} doesn't need a target")
        super().__init__(action_model, players)
