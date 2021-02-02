import logging
from enum import auto
from enum import Enum
from typing import Callable
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import Type
from typing import Union

import pydantic

from ..model import GameStage
from ..model import PlayerRole
from ..model import PlayerState
from ..resolver import GameAction
from .teams import Team


class StageAction(pydantic.BaseModel):
    text: Dict[PlayerState, str]
    button_text: Optional[str]
    select_person = True

    @pydantic.validator("text", pre=True)
    def build_text(cls, v):

        # If text for only one PlayerState has been provided, turn it into a dict for all states
        if not isinstance(v, dict):
            v = {state: v for state in list(PlayerState)}

        else:
            # If a default entry was provided, use it to fill in missing roles
            for state in list(PlayerState):
                if state not in v:
                    if "default" in v:
                        v[state] = v["default"]
                    else:
                        raise KeyError("Not all PlayerStates defined")

            if "default" in v:
                del v["default"]

        return v


class RoleDescription(pydantic.BaseModel):
    display_name: str
    fallback_role: Optional[PlayerRole]
    fallback_role_description: Optional["RoleDescription"]
    stages: Dict[GameStage, StageAction]

    class SecretChatType(Enum):
        TEAM = auto()
        ROLE = auto()

    secret_chat_enabled: Optional[SecretChatType]

    # If present, announce to this role who else has this role.
    # Use this text to do so (e.g. "fellow wolves" -> "your fellow wolves are x and y")
    reveal_others_text = ""

    # dict of stages in which this role cannot see their own role,
    # and sees themselves as the given role instead
    masked_role_in_stages: Dict[GameStage, PlayerRole] = {}

    @pydantic.validator("fallback_role_description", always=True)
    def role_and_desc(cls, v, values):
        if v and ("fallback_role" not in values or not values["fallback_role"]):
            raise ValueError("fallback_role_description provided without fallback_role")
        return v

    @pydantic.validator("stages")
    def all_stages(cls, v, values):

        if not v:
            v = {}

        # Check that this role either has something defined in all the stages or has a fallback
        if not (
            "fallback_role_description" in values
            and values["fallback_role_description"]
        ):
            for stage in list(GameStage):
                if stage not in v:
                    raise ValueError(
                        f"stage {stage} not present and no fallback provided"
                    )

        return v

    def get_stage_action(self, stage: GameStage) -> StageAction:
        """Get the StageAction for this stage, getting values from the role or fallback role as required.

        To do this, first get the main StageAction. If there isn't one, get the fallback StageAction. If
        there is one but there's no button text, get the button text from the fallback role if there is any.
        """
        if stage in self.stages:
            stage_action = self.stages[stage].copy()
            if not stage_action.button_text and self.fallback_role_description:
                fallback_desc = self.fallback_role_description.get_stage_action(stage)

                stage_action.button_text = fallback_desc.button_text
                stage_action.select_person = fallback_desc.select_person
        elif self.fallback_role_description:
            stage_action = self.fallback_role_description.get_stage_action(stage)
        else:
            raise KeyError(f"Stage {stage} not present and fallback not provided")

        return stage_action

    team: Team

    class Config:
        allow_mutation = False


RoleDescription.update_forward_refs()


class RoleDetails(pydantic.BaseModel):
    """
    A RoleDetails tuple contains a complete description of what a role entails
    It can be used to figure out how a role should behave and will be stored in
    registration.ROLE_MAP.

    If role_description is a Callable, calling it without arguments should return
    a RoleDescripton
    """

    role_description: Union[RoleDescription, Callable]
    actions: Dict[GameStage, Type[GameAction]] = None
    startup_callback: Callable = None

    class Config:
        arbitrary_types_allowed = True
