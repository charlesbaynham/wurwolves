import logging
from typing import List, Union
from uuid import UUID

import pydantic

from .game import WurwolvesGame
from .model import PlayerState, GameStage


class FrontendState(pydantic.BaseModel):
    '''
    Schema for the React state of a client's frontend
    '''

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
        day_text: str
        night_text: str
        lobby_text: str
        button_visible: bool
        button_enabled: bool
        button_text: Union[None, str] = None
        button_confirm_text: Union[None, str] = None
        button_submit_url: Union[None, str] = None
        button_submit_person: Union[None, bool] = None

    role: RoleState

    myID: UUID


def parse_game_to_state(game_tag: str, user_id: UUID):
    '''
    Gets the requested Game and parses it into a FrontendState for viewing by the user user_id
    '''
    g = WurwolvesGame(game_tag)
    game = g.get_game_model()
    player = g.get_player_model(user_id)

    logging.debug("Game: %s", game)
    logging.debug("Player: %s", player)
    logging.debug("User id: %s", user_id)

    if not game or not player:
        return None

    logging.debug("Game players: %s", game.players)

    state = FrontendState(
        players=[
            FrontendState.PlayerState(
                id=p.user_id,
                name=p.user.name,
                status=p.state,
                selected=False
            ) for p in game.players
        ],
        chat=game.messages,
        stage=game.stage,
        role=FrontendState.RoleState(
            title='Hello',
            day_text='I\'m the daytime',
            night_text='I\'m the nighttime',
            lobby_text='I\'m the lobby',
            button_visible=False,
            button_enabled=False,
        ),
        myID=user_id
    )

    logging.debug("Full UI state: %s", state)

    return state
