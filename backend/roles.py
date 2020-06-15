from typing import Union
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends, Path, HTTPException

from .model import Action, PlayerRole, GameStage
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

    priority: int = 0

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

MEDIC = RoleDescription(
    display_name="Medic",
    night_action=True,
    day_text="""
You are a medic! You get to save one person each night. 

You win if all the wolves are eliminated. 
    """,
    night_text="""
Choose who to save...
    """,
    vote_text=None,
    fallback_role=DEFAULT_ROLE,
)

ROLE_MAP = {
    PlayerRole.VILLAGER: DEFAULT_ROLE,
    PlayerRole.SEER: DEFAULT_ROLE,
    PlayerRole.MEDIC: MEDIC,
    PlayerRole.WOLF: DEFAULT_ROLE,
    PlayerRole.SPECTATOR: DEFAULT_ROLE,
}


class MedicMixin():
    def medic_action(self, payload):
        print(payload)


def named(role_name):
    def f(func):
        func.__name__ = f"{role_name}_action"
        func.__doc__ = ('An automatically registered function to perform '
                        f'the action associated with the {role_name} role')
        return func
    return f


def register(WurwolvesGame, role_name, role: PlayerRole):
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

        if not game:
            raise HTTPException(status_code=404, detail=f"Game {self.game_id} not found")

        # Check if this user is entitled to act in this capacity
        player = self.get_player(user_id)
        if not player:
            raise HTTPException(status_code=404, detail=f"Player {user_id} not found")
        if player.role != role:
            raise HTTPException(status_code=403, detail=f"Player {user_id} is not a {role}")
        if not ROLE_MAP[role].night_action:
            raise HTTPException(status_code=403, detail=f"Player {user_id} in role {role} has no night action")
        if not game.stage == GameStage.NIGHT:
            raise HTTPException(status_code=403, detail="Actions may only be performed at night")

        # Check if this player has already acted this round
        action = self._session.query(Action).filter(
            Action.game_id == game.id,
            Action.stage_id == game.stage_id,
            Action.player_id == player.id
        ).first()

        if action:
            raise HTTPException(
                status_code=403,
                detail=f"Action already completed for player {user_id} in round {game.stage_id}"
            )

        # Save the action
        action = Action(
            game_id=self.game_id,
            player_id=player.id,
            selected_id=selected_id,
            stage_id=game.stage_id,
        )
        self._session.add(action)

        # If all the actions are complete, process them
        players = game.players
        ready = True
        for player in players:
            if (ROLE_MAP[player.role].night_action and
                    not any(a.stage_id == game.stage_id for a in player.actions)):
                ready = False
                break

        if ready:
            self.process_actions()

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
