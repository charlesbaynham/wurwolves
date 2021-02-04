from typing import TYPE_CHECKING

from fastapi import HTTPException

from ..model import GameStage
from ..model import PlayerState
from ..resolver import ActionMixin
from ..resolver import GameAction

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

        out = not bool(previous_actions)

        if hasattr(super(), "is_action_available"):
            out = out and super().is_action_available(game, stage, stage_id, player_id)

        return out


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


class TargetMustBeAlive(TargetRequired, ActionMixin):
    @classmethod
    def immediate(cls, game: "WurwolvesGame" = None, selected_id=None, **kwargs):
        selected_player = game.get_player_model(selected_id)

        if selected_player.state != PlayerState.ALIVE:
            raise HTTPException(403, "Your target must be alive")

        super().immediate(game=game, selected_id=selected_id, **kwargs)


class TargetMustNotBeSelf(TargetRequired, ActionMixin):
    @classmethod
    def immediate(cls, user_id=None, selected_id=None, **kwargs):
        if user_id == selected_id:
            raise HTTPException(403, "You cannot choose yourself")

        super().immediate(user_id=user_id, selected_id=selected_id, **kwargs)
