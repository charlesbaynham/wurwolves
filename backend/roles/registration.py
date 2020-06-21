import logging
from functools import partial
from typing import TYPE_CHECKING, Dict, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path

from ..model import Action, GameStage, PlayerRole, PlayerState
from ..user_id import get_user_id
from . import jester, medic, seer, spectator, villager, wolf
from .common import RoleDetails

if TYPE_CHECKING:
    from ..resolver import GameAction

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
jester.register(ROLE_MAP)

if any(r not in ROLE_MAP for r in list(PlayerRole)):
    raise TypeError("Not all roles are registered")


def get_action_func_name(role: PlayerRole, stage: GameStage):
    return f"{role.value.lower()}_{stage.value.lower()}_action"


def get_role_team(role: PlayerRole):
    return ROLE_MAP[role].role_description.team


def get_role_action(role: PlayerRole, stage: GameStage) -> Union[None, "GameAction"]:
    """ Get the action class associated with a role and stage, or None """
    role_details = ROLE_MAP[role]

    action_class = None
    if role_details.actions and stage in role_details.actions:
        action_class = role_details.actions[stage]
    elif role_details.role_description.fallback_role:
        fallback_role_details = ROLE_MAP[role_details.role_description.fallback_role]
        if (
            fallback_role_details
            and fallback_role_details.actions
            and stage in fallback_role_details.actions
        ):
            action_class = fallback_role_details.actions[stage]
        else:
            action_class = None

    return action_class


def named(n):
    def f(func):
        func.__name__ = f"{n}_action"
        func.__doc__ = (
            "An automatically registered function to perform "
            f"the action associated with the {n} role"
        )
        return func

    return f


def register_role(WurwolvesGame, role: PlayerRole):
    """
    Register a new role by creating an API endpoint at <role_name>_action which calls a new method on
    WurwolvesGame called the same.

    The API endpoint is added to the router in this module which must be imported by main
    """

    role_description = ROLE_MAP[role].role_description

    for stage in list(GameStage):
        #  Check if there's a role action for this stage
        if not get_role_action(role, stage):
            if role_description.get_stage_action(stage).button_text:
                raise ValueError(
                    f"Role {role} has no action in {stage} but the button is set to visible"
                )
            continue

        # Confirm that the button is displayed
        if not role_description.get_stage_action(stage).button_text:
            raise ValueError(
                f"Role {role} has a {stage} action but the button is not displayed"
            )

        func_name = get_action_func_name(role, stage)

        logging.info(f"Registering {func_name} for {stage}")

        # Define a function to be added to WurwolvesGame
        @WurwolvesGame.db_scoped
        @named(func_name)
        def game_func(
            self: WurwolvesGame,
            user_id: UUID,
            selected_id: UUID = None,
            stage=stage,  # This odd keyword argument forces early binding of stage:
            # otherwise it will be evaulated once this function runs.
            # See https://docs.python-guide.org/writing/gotchas/#late-binding-closures
        ):

            game = self.get_game()

            # Save the stage ID now in case the immediate actions change it
            stage_id = game.stage_id

            if not game:
                raise HTTPException(
                    status_code=404, detail=f"Game {self.game_id} not found"
                )

            # Check if this user is entitled to act in this capacity
            player = self.get_player(user_id)
            if not player:
                raise HTTPException(
                    status_code=404, detail=f"Player {user_id} not found"
                )
            if player.role != role:
                raise HTTPException(
                    status_code=403, detail=f"Player {user_id} is not a {role}"
                )
            if not get_role_action(role, stage):
                raise HTTPException(
                    status_code=403,
                    detail=f"Player {user_id} in role {role} has no action in stage {stage}",
                )
            if not game.stage == stage:
                raise HTTPException(
                    status_code=403,
                    detail=f"Action {func_name} is not valid in stage {game.stage}, only in {stage}",
                )

            # Check if this player has already acted this round
            if (
                self._session.query(Action)
                .filter(
                    Action.game_id == game.id,
                    Action.stage_id == game.stage_id,
                    Action.player_id == player.id,
                )
                .first()
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"Action already completed for player {user_id} in round {game.stage_id}",
                )

            if selected_id:
                selected_player_id = self.get_player(selected_id).id
            else:
                selected_player_id = None

            # Save the action
            action = Action(
                game_id=self.game_id,
                player_id=player.id,
                selected_player_id=selected_player_id,
                stage_id=game.stage_id,
            )
            self._session.add(action)

            # Perform any immediate actions registered
            action_class = get_role_action(player.role, game.stage)
            if action_class:
                action_class.immediate(
                    game=self, user_id=user_id, selected_id=selected_id
                )

            # If all the actions are complete, process them
            players = game.players
            ready = True
            for player in players:
                if (
                    get_role_action(
                        player.role, stage
                    )  # Player has an action in this stage...
                    and (player.state == PlayerState.ALIVE)  #  ...isn't dead
                    and not any(
                        a.stage_id == stage_id for a in player.actions
                    )  #  ..and hasn't yet acted
                ):
                    ready = False
                    break

            if ready:
                self.process_actions(stage, stage_id)

            self.get_game().touch()

        # Make one for the API router that does / does not require a selected_id
        if role_description.get_stage_action(stage).select_person:

            def api_func(
                func_name,  #  For early binding
                selected_id: UUID,
                game_tag: str = Path(..., title="The four-word ID of the game"),
                user_id=Depends(get_user_id),
            ):
                g = WurwolvesGame(game_tag)
                f = getattr(WurwolvesGame, func_name)
                f(g, user_id, selected_id)

        else:

            def api_func(
                func_name,  #  For early binding
                game_tag: str = Path(..., title="The four-word ID of the game"),
                user_id=Depends(get_user_id),
            ):
                g = WurwolvesGame(game_tag)
                f = getattr(WurwolvesGame, func_name)
                f(g, user_id)

        # Force early binding of the func_name by using partial
        bound_api_func = partial(api_func, func_name)
        bound_api_func = named(func_name)(bound_api_func)

        # Register it with the API router
        router.post(f"/{{game_tag}}/{func_name}")(bound_api_func)

        # Patch the WurwolvesGame function into WurwolvesGame: the API
        # function is in the router which will be added in main
        setattr(WurwolvesGame, func_name, game_func)
