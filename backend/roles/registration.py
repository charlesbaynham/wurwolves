from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path

from ..model import Action, GameStage, PlayerRole
from ..user_id import get_user_id
from . import medic, seer, villager, wolf, spectator
from .common import RoleDetails

router = APIRouter()


# The ROLE_MAP maps PlayerRoles to RoleDetails. It is therefore a way of looking
# up how a role should behave given it a PlayerRole enum
ROLE_MAP: Dict[PlayerRole, RoleDetails] = {}


# Populate ROLE_MAP
medic.register(ROLE_MAP)
seer.register(ROLE_MAP)
villager.register(ROLE_MAP)
wolf.register(ROLE_MAP)
spectator.register(ROLE_MAP)

if any(r not in ROLE_MAP for r in list(PlayerRole)):
    raise TypeError("Not all roles are registered")


def get_action_func_name(role: PlayerRole):
    return f"{role.value.lower()}_action"


def named(n):
    def f(func):
        func.__name__ = f"{n}_action"
        func.__doc__ = ('An automatically registered function to perform '
                        f'the action associated with the {n} role')
        return func
    return f


def register_role(WurwolvesGame, role: PlayerRole):
    """
    Register a new role by creating an API endpoint at <role_name>_action which calls a new method on
    WurwolvesGame called the same.

    The API endpoint is added to the router in this module which must be imported by main
    """

    func_name = get_action_func_name(role)

    # Define a function to be added to WurwolvesGame
    @ WurwolvesGame.db_scoped
    @ named(func_name)
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
        if not ROLE_MAP[role].role_description.night_action:
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
            selected_player_id=selected_id,
            stage_id=game.stage_id,
        )
        self._session.add(action)

        # If all the actions are complete, process them
        players = game.players
        ready = True
        for player in players:
            if (ROLE_MAP[player.role].role_description.night_action and
                    not any(a.stage_id == game.stage_id for a in player.actions)):
                ready = False
                break

        if ready:
            self.process_actions()

        game.touch()

    # And one for the API router
    @router.get(f"/{{game_tag}}/{func_name}")
    @named(func_name)
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
