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
    def fallback_undefined(cls, v, values):
        if values["fallback_role"] and values["fallback_role"].stages:
            fallback = values["fallback_role"].stages
        else:
            fallback = {}

        if not v:
            v = {}

        out = {**fallback, **v}

        # Check that this role has something defined in all the stages,
        # except don't worry if the lobby isn't defined
        for stage in list(GameStage):
            if not (stage in out or stage is GameStage.LOBBY):
                raise ValueError(f"stage {stage} not present")

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
    actions: Dict[GameStage, GameAction] = None
