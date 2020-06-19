from enum import Enum
from typing import NamedTuple, Optional, Dict

import pydantic

from ..model import GameStage
from ..resolver import GameAction


class StageAction(pydantic.BaseModel):
    text: str
    button_text: Optional[str]
    select_person = True


class RoleDescription(pydantic.BaseModel):
    display_name: str
    fallback_role: Optional["RoleDescription"]
    stages: Dict[GameStage, StageAction]
    priority: int = 0

    @pydantic.validator("stages")
    def all_stages_defined(cls, v, values):
        if values["fallback_role"] and values["fallback_role"].stages:
            fallback = values["fallback_role"].stages
        else:
            fallback = {}

        if not v:
            v = {}

        out = v
        out.update(fallback)

        for stage in list(GameStage):
            assert stage in out

        return out

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
    actions: Optional[Dict[GameStage, GameAction]]


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
    """, button_text="Start game", select_person=False,
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
        GameStage.VOTING: StageAction(
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
