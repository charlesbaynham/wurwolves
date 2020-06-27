import logging
from functools import partial
from typing import TYPE_CHECKING, Callable, Dict, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path

from ..model import Action, GameStage, PlayerRole
from ..user_id import get_user_id
from . import jester, medic, narrator, seer, spectator, villager, wolf
from .common import RoleDescription, RoleDetails

if TYPE_CHECKING:
    from ..resolver import GameAction

router = APIRouter()


# The ROLE_MAP maps PlayerRoles to RoleDetails. It is therefore a way of looking
# up how a role should behave given it a PlayerRole enum.
ROLE_MAP: Dict[PlayerRole, RoleDetails] = {}

# Populate ROLE_MAP
medic.register(ROLE_MAP)
seer.register(ROLE_MAP)
villager.register(ROLE_MAP)
wolf.register(ROLE_MAP)
spectator.register(ROLE_MAP)
jester.register(ROLE_MAP)
narrator.register(ROLE_MAP)

if any(r not in ROLE_MAP for r in list(PlayerRole)):
    raise TypeError("Not all roles are registered with roles.registration")


registered_with_game = []


def get_role_description(role) -> RoleDescription:
    desc = ROLE_MAP[role].role_description
    if callable(desc):
        desc = desc()
    return desc


def get_action_func_name(role: PlayerRole, stage: GameStage):
    return f"{role.value.lower()}_{stage.value.lower()}_action"


def get_role_team(role: PlayerRole):
    return get_role_description(role).team


def get_role_actions(role: PlayerRole):
    return ROLE_MAP[role].actions


def get_role_action(role: PlayerRole, stage: GameStage) -> Union[None, "GameAction"]:
    """ Get the action class associated with a role and stage, or None """
    role_description = get_role_description(role)
    role_actions = get_role_actions(role)

    action_class = None
    if role_actions and stage in role_actions:
        action_class = role_actions[stage]
    elif role_description.fallback_role:
        action_class = get_role_action(role_description.fallback_role, stage)

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


def register_roles(WurwolvesGame):
    """
    Register all roles by creating an API endpoint at <role_name>_action which calls a new method on
    WurwolvesGame called the same.
    """
    for role in list(PlayerRole):
        register_role(WurwolvesGame, role)


def register_role(WurwolvesGame, role: PlayerRole):
    """
    Register a new role by creating an API endpoint at <role_name>_action which calls a new method on
    WurwolvesGame called the same.

    The API endpoint is added to the router in this module which must be imported by main
    """

    registered_with_game.append(role)

    role_description = get_role_description(role)

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
            # otherwise it will be evaluated once this function runs.
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

            action_class = get_role_action(player.role, game.stage)

            if not action_class:
                raise HTTPException(
                    status_code=403,
                    detail=f"Player {user_id} in role {role} has no action in stage {stage}",
                )
            if player.state not in action_class.allowed_player_states:
                raise HTTPException(
                    status_code=403,
                    detail=f"Player {user_id} is not in the right state",
                )
            if not game.stage == stage:
                raise HTTPException(
                    status_code=403,
                    detail=f"Action {func_name} is not valid in stage {game.stage}, only in {stage}",
                )

            # Check if this player has already acted this round
            has_action, action_enabled = self.player_has_action(
                player, game.stage, game.stage_id
            )
            if not action_enabled:
                raise HTTPException(
                    status_code=403,
                    detail=f"Action already completed / disabled for player {user_id} in round {game.stage_id}",
                )

            if selected_id:
                selected_player_id = self.get_player(selected_id).id
            else:
                selected_player_id = None

            # Save the action
            # Do this as a subtransaction so that the "all actions finished"
            # query has access to this action, but touch the game so an update
            # is triggered
            self._session.begin_nested()
            action = Action(
                game_id=self.game_id,
                player_id=player.id,
                selected_player_id=selected_player_id,
                stage_id=stage_id,
            )
            self._session.add(action)
            self._session.commit()

            # Perform any immediate actions registered
            if action_class:
                action_class.immediate(
                    game=self, user_id=user_id, selected_id=selected_id
                )

            # If all the actions are complete, process them
            # Note that game.stage / game.stage_id may have been changed by the immediate actions,
            # so we use the saved versions here which have not changed.
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
