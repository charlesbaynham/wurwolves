import logging
from typing import Dict, List, Union
from uuid import UUID

import pydantic

from .game import WurwolvesGame
from .model import GameStage, PlayerState
from .roles import ROLE_MAP


class FrontendState(pydantic.BaseModel):
    '''
    Schema for the React state of a client's frontend
    '''

    state_hash: int

    class PlayerState(pydantic.BaseModel):
        id: UUID
        name: str
        status: PlayerState
        selected: bool = False

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
            logging.warning(f"Text = : {v}")
            logging.warning(f"Values = {values}")
            if values["button_visible"] and not v:
                raise ValueError("No button text provided when button is visible")
            return v

    roles: Dict[GameStage, RoleState]

    @pydantic.validator('roles')
    def role_for_all_stages(cls, v):
        for stage in list(GameStage):
            if stage not in v:
                raise ValueError('role must contain an entry for all stages. {} is missing'.format(stage))
        return v

    myID: UUID
    myName: str
    myNameIsGenerated: bool


def parse_game_to_state(game_tag: str, user_id: UUID):
    '''
    Gets the requested Game and parses it into a FrontendState for viewing by the user user_id
    '''
    g = WurwolvesGame(game_tag)
    game = g.get_game_model()
    player = g.get_player_model(user_id)

    logging.info("Game: %s", game)
    logging.info("Player: %s", player)
    logging.info("User id: %s", user_id)

    if not game or not player:
        return None

    logging.debug("Game players: %s", game.players)

    role_details = ROLE_MAP[player.role].role_description

    state = FrontendState(
        state_hash=game.update_counter,
        players=[
            FrontendState.PlayerState(
                id=p.user_id,
                name=p.user.name,
                status=p.state,
                selected=False
            ) for p in game.players
        ],
        chat=[
            FrontendState.ChatMsg(
                msg=m.text,
                isStrong=m.is_strong
            ) for m in game.messages if (not m.visible_to) or any(player.id == v.id for v in m.visible_to)
        ],
        stage=game.stage,
        roles={
            GameStage.LOBBY: FrontendState.RoleState(
                title=role_details.display_name,
                text=role_details.day_text or role_details.fallback_role.day_text,
                button_visible=True,
                button_enabled=True,
                button_submit_func='start_game',
                button_text="Start game"
            ),
            GameStage.DAY: FrontendState.RoleState(
                title=role_details.display_name,
                text=role_details.day_text or role_details.fallback_role.day_text,
                button_visible=False,
                button_enabled=False,
            ),
            GameStage.VOTING: FrontendState.RoleState(
                title=role_details.display_name,
                text=role_details.vote_text or role_details.fallback_role.vote_text,
                button_visible=True,
                button_enabled=True,
                button_text=role_details.vote_button_text or role_details.fallback_role.vote_button_text,
            ),
            GameStage.NIGHT: FrontendState.RoleState(
                title=role_details.display_name,
                text=role_details.night_text or role_details.fallback_role.night_text,
                button_visible=role_details.night_action,
                button_enabled=role_details.night_action,
                button_text=role_details.night_button_text,
            ),
        },
        myID=user_id,
        myName=player.user.name,
        myNameIsGenerated=player.user.name_is_generated,
    )

    logging.debug("Full UI state: %s", state)

    return state
