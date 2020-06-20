from enum import Enum
from typing import Dict, NamedTuple, Optional

import pydantic

from ..model import GameStage, PlayerRole
from ..resolver import GameAction


class StageAction(pydantic.BaseModel):
    text: str
    button_text: Optional[str]
    select_person = True


class RoleDescription(pydantic.BaseModel):
    display_name: str
    fallback_role: Optional[PlayerRole]
    fallback_role_description: Optional["RoleDescription"]
    stages: Dict[GameStage, StageAction]
    priority: int = 0

    @pydantic.validator("fallback_role_description")
    def role_and_desc(cls, v, values):
        if not values["fallback_role"]:
            raise ValueError("fallback_role_description provided without fallback_role")
        return v

    @pydantic.validator("fallback_role")
    def role_and_desc_2(cls, v, values):
        if not values["fallback_role_description"]:
            raise ValueError("fallback_role provided without fallback_role_description")
        return v

    @pydantic.validator("stages")
    def all_stages(cls, v, values):
        print(values)
        if (
            "fallback_role_description" in values
            and values["fallback_role_description"]
            and values["fallback_role_description"].stages
        ):
            fallback = values["fallback_role_description"].stages
        else:
            fallback = {}

        if not v:
            v = {}

        out = {**fallback, **v}

        # Check that this role has something defined in all the stages
        for stage in list(GameStage):
            if stage not in out:
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
