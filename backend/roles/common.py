from enum import Enum
from typing import NamedTuple, Union

import pydantic

from ..resolver import GameAction


class RoleDescription(pydantic.BaseModel):
    display_name: str

    night_action: bool
    night_action_url: Union[None, str] = None
    night_action_select_person = True
    night_button_text: Union[None, str] = None
    vote_button_text: Union[None, str] = None

    lobby_text: Union[None, str] = None
    day_text: Union[None, str] = None
    night_text: Union[None, str] = None
    vote_text: Union[None, str] = None

    priority: int = 0

    class Team(Enum):
        VILLAGERS = 'VILLAGERS'
        WOLVES = 'WOLVES'
        SPECTATORS = 'SPECTATORS'
        JESTER = "JESTER"
    team: Team

    fallback_role: Union[None, "RoleDescription"]

    class Config:
        allow_mutation = False


RoleDescription.update_forward_refs()


class RoleDetails(NamedTuple):
    '''
    A RoleDetails tuple contains a complete description of what a role entails
    It can be used to figure out how a role should behave and will be stored in
    .registration.ROLE_MAP
    '''
    role_description: RoleDescription
    role_action: GameAction


DEFAULT_ROLE = RoleDescription(
    display_name="Villager",
    night_action=False,
    lobby_text="""
Welcome to Wurwolves! 
The game hasn't started yet: you'll need at least 5 players for the game to be playable,
but it's more fun with 7 or more. Once everyone has joined, press the \"Start game\" button. 

To invite more people, just send them the link to this page. 

This website is designed for playing with people you already know:
it handles the gameplay but you'll also need to communicate so you
can argue and discuss what happens. If you're not in the same room,
you should probably start a video call. 
    """,
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
    vote_button_text="Vote for someone to lynch...",
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=None,
)


