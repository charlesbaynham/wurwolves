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

    day_text: Union[None, str] = None
    night_text: Union[None, str] = None
    vote_text: Union[None, str] = None

    priority: int = 0

    class Team(Enum):
        VILLAGERS = 'VILLAGERS'
        WOLVES = 'WOLVES'
        SPECTATORS = 'SPECTATORS'
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
