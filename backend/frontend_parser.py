import logging
import random
import time
from typing import List
from typing import Union
from uuid import UUID

import pydantic

from . import database
from .game import WurwolvesGame
from .model import GameStage
from .model import PlayerRole
from .model import PlayerState
from .roles import get_action_func_name
from .roles import get_role_description


class FrontendState(pydantic.BaseModel):
    """
    Schema for the React state of a client's frontend
    """

    state_hash: int

    class UIPlayerState(pydantic.BaseModel):
        id: UUID
        name: str
        # Player state. One of PlayerState
        status: str
        # PlayerRole to display. Players will appear as villagers unless they should be revealed
        role: str
        # Random float from 0-1.
        # Will be used by the frontend to decide which picture to display if multiple are available
        seed: float
        # Show this player as having completed their actions this round
        ready: bool = False

        @pydantic.validator("status")
        def status_valid(cls, v):
            try:
                PlayerState(v)
            except ValueError:
                assert v in ["MAYOR"]
            return v

        @pydantic.validator("role")
        def role_valid(cls, v):
            PlayerRole(v)
            return v

    players: List[UIPlayerState]

    class ChatMsg(pydantic.BaseModel):
        msg: str
        isStrong = False

    chat: List[ChatMsg]
    showSecretChat = False

    stage: GameStage

    class RoleState(pydantic.BaseModel):
        title: str
        text: str
        role: str
        button_visible: bool
        button_enabled: bool
        button_text: Union[None, str] = None
        button_confirm_text: Union[None, str] = None
        button_submit_func: Union[None, str] = None
        button_submit_person: Union[None, bool] = None

        seed: float

        @pydantic.validator("role")
        def role_valid(cls, v):
            PlayerRole(v)
            return v

        @pydantic.validator("button_text", always=True)
        def text_present(cls, v, values):
            logging.debug(f"Text = : {v}")
            logging.debug(f"Values = {values}")
            if values["button_visible"] and not v:
                raise ValueError("No button text provided when button is visible")
            return v

    controls_state: RoleState

    myID: UUID
    myName: str
    myNameIsGenerated: bool


def parse_game_to_state(game_tag: str, user_id: UUID) -> FrontendState:
    """
    Gets the requested Game and parses it into a FrontendState for viewing by the user user_id
    """

    logging.debug(f"Starting parse_game_to_state at: {time.time()}")

    g = WurwolvesGame(game_tag)

    game = g.get_game_model()

    if not game:
        g.join(user_id)
        game = g.get_game_model()

    actions = g.get_actions_model()

    players = game.players

    logging.debug(f"Point 2: {time.time()}")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("Players: %s", [p.user.name for p in players])

    try:
        player = [p for p in players if p.user_id == user_id][0]
    except IndexError:
        g.join(user_id)
        game = g.get_game_model()

        player = [p for p in players if p.user_id == user_id][0]

    logging.debug(f"Point 3: {time.time()}")

    logging.debug("Game: %s", game)
    logging.debug("Player: %s", player)
    logging.debug("User id: %s", user_id)
    logging.debug("Game players: %s", players)

    role_details = get_role_description(player.role)

    logging.debug(f"Point 4: {time.time()}")

    action_desc = role_details.get_stage_action(game.stage)

    logging.debug(f"Point 5: {time.time()}")

    has_action, action_enabled = g.player_has_action(
        player.id, game.stage, game.stage_id
    )

    logging.debug(f"Point 6: {time.time()}")

    logging.debug(
        f"Player {player.user.name} is a {player.role.value}, has_action={has_action}, action_enabled={action_enabled}"
    )

    controls_state = FrontendState.RoleState(
        title=role_details.display_name,
        text=action_desc.text[player.state],
        role=player.role,
        seed=player.seed,
        button_visible=has_action,
        button_enabled=action_enabled,
        button_text=action_desc.button_text,
        button_submit_person=action_desc.button_text and action_desc.select_person,
        button_submit_func=get_action_func_name(player.role, game.stage),
    )

    logging.debug(f"Point 7: {time.time()}")

    logging.debug("role_details.stages: {}".format(role_details.stages))
    logging.debug("action_desc: {}".format(action_desc))
    logging.debug("controls_state: {}".format(controls_state))

    player_states = []
    for p in players:
        logging.debug(f"Point 8: {time.time()}")
        status = p.state

        ready = False
        if game.stage in [
            GameStage.LOBBY,
            GameStage.ENDED,
            GameStage.VOTING,
            GameStage.DAY,
        ]:
            has_action, action_enabled = g.player_has_action(
                p.id, game.stage, game.stage_id
            )
            if has_action and not action_enabled:
                ready = True

        # Display real role if the game is ended or this player should be able to see it
        real_role = p.role
        if (
            p.previous_role
            and (p.role == PlayerRole.SPECTATOR or p.role == PlayerRole.NARRATOR)
            and p.state != PlayerState.SPECTATING
        ):
            real_role = p.previous_role
        displayed_role = PlayerRole.VILLAGER

        # Only display as a spectator if the player is a spectator/narrator and had no
        # previous role
        if real_role == PlayerRole.SPECTATOR or real_role == PlayerRole.NARRATOR:
            displayed_role = PlayerRole.SPECTATOR
        elif (
            (p.id == player.id)
            or player.role == PlayerRole.NARRATOR
            or (real_role == PlayerRole.WOLF and player.role == PlayerRole.WOLF)
            or (real_role == PlayerRole.ACOLYTE and player.role == PlayerRole.WOLF)
            or (real_role == PlayerRole.JESTER and player.role == PlayerRole.WOLF)
            or (real_role == PlayerRole.MASON and player.role == PlayerRole.MASON)
            or (real_role == PlayerRole.JESTER and p.state == PlayerState.LYNCHED)
            or game.stage == GameStage.ENDED
            or (
                real_role == PlayerRole.MAYOR
                and g.num_previous_stages(GameStage.NIGHT, game.stage_id) > 0
            )
        ):
            displayed_role = real_role

        player_states.append(
            FrontendState.UIPlayerState(
                id=p.user_id,
                name=p.user.name,
                status=status,
                role=displayed_role,
                seed=p.seed,
                selected=False,
                ready=ready,
            )
        )

    # Random sort
    player_states.sort(key=lambda s: s.seed)

    logging.debug(f"Point 9: {time.time()}")

    state = FrontendState(
        state_hash=game.update_tag,
        players=player_states,
        chat=[
            FrontendState.ChatMsg(msg=m.text, isStrong=m.is_strong)
            for m in game.messages
            if (not m.visible_to) or any(player.id == v.id for v in m.visible_to)
        ],
        showSecretChat=bool(role_details.secret_chat_enabled),
        stage=game.stage,
        controls_state=controls_state,
        myID=user_id,
        myName=player.user.name,
        myNameIsGenerated=player.user.name_is_generated,
    )

    logging.debug(f"Point 10: {time.time()}")

    logging.debug("Full UI state: %s", state)

    return state
