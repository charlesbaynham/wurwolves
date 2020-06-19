from enum import Enum
from typing import NamedTuple, Optional, Union, Dict

import pydantic

from ..model import GameStage
from ..resolver import GameAction


class StageAction(pydantic.BaseModel):
    text: str
    button_text: Optional[str]
    select_person = True


class RoleDescription(pydantic.BaseModel):
    display_name: str
    fallback_role: Union[None, "RoleDescription"]
    stages = Dict[GameStage, StageAction]
    priority: int = 0

    @pydantic.validator("stages")
    def all_stages_defined(cls, v, values):
        for stage in list(GameStage):
            assert stage in v or stage in values["fallback_role"].stages
        v.update(values["fallback_role"].stages)
        return v

    class Team(Enum):
        VILLAGERS = "VILLAGERS"
        WOLVES = "WOLVES"
        SPECTATORS = "SPECTATORS"
        JESTER = "JESTER"

    team: Team

    class Config:
        allow_mutation = False


RoleDescription.update_forward_refs()


class RoleDetails(NamedTuple):
    """
    A RoleDetails tuple contains a complete description of what a role entails
    It can be used to figure out how a role should behave and will be stored in
    .registration.ROLE_MAP
    """

    role_description: RoleDescription
    role_action: GameAction


DEFAULT_ROLE = RoleDescription(
    display_name="Villager",
    stages={
        GameStage.LOBBY: StageAction(
            text="""
Welcome to Wurwolves! 
The game hasn't started yet: you'll need at least 5 players for the game to be playable,
but it's more fun with 7 or more. Once everyone has joined, press the \"Start game\" button. 

To invite more people, just send them the link to this page. 

This website is designed for playing with people you already know:
it handles the gameplay but you'll also need to communicate so you
can argue and discuss what happens. If you're not in the same room,
you should probably start a video call. 
    """
        ),
        GameStage.DAY: StageAction(
            text="""
You are a villager. You have no special powers. Try not to get eaten!

You win if all the wolves are eliminated. 
    """
        ),
        GameStage.NIGHT: StageAction(
            text="""
You have nothing to do at night. Relax...
    """
        ),
        GameStage.VOTE: StageAction(
            text="""
Vote for someone to lynch! Whoever gets the most votes will be killed.

Click someone's icon and click the button. 
    """,
            button_text="Vote for someone to lynch...",
        ),
    },
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=None,
)
