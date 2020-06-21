from .roles import get_action_func_name
import logging
from typing import List, Union
from uuid import UUID

import pydantic

from .game import WurwolvesGame
from .model import GameStage, PlayerState
from .roles import ROLE_MAP, get_role_action


class FrontendState(pydantic.BaseModel):
    """
    Schema for the React state of a client's frontend
    """

    state_hash: int

    class PlayerState(pydantic.BaseModel):
        id: UUID
        name: str
        status: PlayerState

    players: List[PlayerState]

    class ChatMsg(pydantic.BaseModel):
        msg: str
        isStrong = False

    chat: List[ChatMsg]

    stage: GameStage

    class RoleState(pydantic.BaseModel):
        title: str
        text: str
        button_visible: bool
        button_enabled: bool
        button_text: Union[None, str] = None
        button_confirm_text: Union[None, str] = None
        button_submit_func: Union[None, str] = None
        button_submit_person: Union[None, bool] = None

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


def parse_game_to_state(g: WurwolvesGame, user_id: UUID) -> FrontendState:
    """
    Gets the requested Game and parses it into a FrontendState for viewing by the user user_id
    """

    game = g.get_game_model()
    player = g.get_player_model(user_id)

    if not game or not player:
        g.join(user_id)
        game = g.get_game_model()
        player = g.get_player_model(user_id)

    actions = g.get_actions_model(player_id=player.id)

    logging.debug("Game: %s", game)
    logging.debug("Player: %s", player)
    logging.debug("User id: %s", user_id)

    if not game or not player:
        return None

    logging.debug("Game players: %s", game.players)

    role_details = ROLE_MAP[player.role].role_description

    state = role_details.get_stage_action(game.stage)

    controls_state = FrontendState.RoleState(
        title=role_details.display_name,
        text=state.text,
        button_visible=bool(state.button_text),
        button_enabled=(
            bool(state.button_text)
            and not actions
            and player.state
            in get_role_action(player.role, game.stage).allowed_player_states
        ),
        button_text=state.button_text,
        button_submit_person=state.select_person,
        button_submit_func=get_action_func_name(player.role, game.stage),
    )

    logging.debug("role_details.stages: {}".format(role_details.stages))
    logging.debug("state: {}".format(state))
    logging.debug("controls_state: {}".format(controls_state))

    state = FrontendState(
        state_hash=game.update_counter,
        players=[
            FrontendState.PlayerState(
                id=p.user_id, name=p.user.name, status=p.state, selected=False
            )
            for p in game.players
        ],
        chat=[
            FrontendState.ChatMsg(msg=m.text, isStrong=m.is_strong)
            for m in game.messages
            if (not m.visible_to) or any(player.id == v.id for v in m.visible_to)
        ],
        stage=game.stage,
        controls_state=controls_state,
        myID=user_id,
        myName=player.user.name,
        myNameIsGenerated=player.user.name_is_generated,
    )

    logging.debug("Full UI state: %s", state)

    return state
