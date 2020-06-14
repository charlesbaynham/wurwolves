from typing import Union
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends, Path, HTTPException

from .model import Action, PlayerRole
from .user_id import get_user_id

router = APIRouter()


class RoleDescription(pydantic.BaseModel):
    display_name: str

    night_action: bool
    night_action_url: Union[None, str] = None
    night_action_select_person = True
    night_button_text: Union[None, str] = None

    day_text: Union[None, str] = None
    night_text: Union[None, str] = None
    vote_text: Union[None, str] = None

    fallback_role: Union[None, "RoleDescription"]


RoleDescription.update_forward_refs()

DEFAULT_ROLE = RoleDescription(
    display_name="Villager",
    night_action=False,
    day_text="""
You are a villager. You have no special powers. Try not to get eaten!

You win if all the wolves are eliminated. 
    """,
    night_text="""
You have nothing to do at night. Relax...
    """,
    vote_text="""
Vote for someone to lynch! Whoever gets the most votes will be killed.

Click someone's icon and click the button. 
    """,
    fallback_role=None,
)


ROLE_MAP = {
    PlayerRole.VILLAGER: DEFAULT_ROLE,
    PlayerRole.SEER: DEFAULT_ROLE,
    PlayerRole.MEDIC: DEFAULT_ROLE,
    PlayerRole.WOLF: DEFAULT_ROLE,
    PlayerRole.SPECTATOR: DEFAULT_ROLE,
}


class MedicMixin():
    def medic_action(self, payload):
        print(payload)


def named(role_name):
    def f(func):
        func.__name__ = f"{role_name}_action"
        func.__docstring__ = f'An automatically registered function to perform the action associated with the {role_name} role'
        return func
    return f


def register(WurwolvesGame, role_name):
    """
    Register a new role by creating an API endpoint at <role_name>_action which calls a new method on 
    WurwolvesGame called the same. 

    The API endpoint is added to the router in this module which must be imported by main
    """

    func_name = f"{role_name}_action"

    # Define a function to be added to WurwolvesGame
    @WurwolvesGame.db_scoped
    @named(role_name)
    def game_func(self: WurwolvesGame, user_id: UUID, selected_id: UUID):

        game = self.get_game()

        # Check if this user is entitled to act at night
        role = self.get_player(user_id).role
        if not ROLE_MAP[role].night_action:
            raise HTTPException(status_code=403, detail=f"Player {user_id} in role {role} has no night action")

        # Check if this user has already acted this round
        action = self._session.query(Action).filter(
            Action.game_id == game.id,
            Action.stage_id == game.stage_id,
            Action.user_id == user_id
        ).first()

        if action:
            raise HTTPException(status_code=403, detail=f"Action already completed for player {user_id} in round {game.stage_id}")

        # Save the action
        action = Action(
            game_id=self.game_id,
            user_id=user_id,
            selected_id=selected_id,
            stage_id=game.stage_id,
        )
        self._session.add(action)

    # And one for the API router
    @router.get(f"/{{game_tag}}/{func_name}")
    @named(role_name)
    def api_func(
        selected_id: UUID = None,
        game_tag: str = Path(..., title="The four-word ID of the game"),
        user_id=Depends(get_user_id),
    ):
        g = WurwolvesGame(game_tag)
        f = getattr(WurwolvesGame, func_name)
        f(g, user_id, selected_id)

    # Patch the WurwolvesGame function into WurwolvesGame: the API
    # function is in the router which will be added in main
    setattr(WurwolvesGame, func_name, game_func)
