"""
The Prostitute role

The Prostitute does two things:

1. They cancel the role of the person they sleep with. That person has
no action that night. If they're a wolf, the wolves only kill if there's
another wolf buddy acting. 

2. They take a person to their house. This means that if the wolves attack
that person, they are not home and so don't die. However if the wolves attack
the prostitute, they get both of them. 
"""
from typing import TYPE_CHECKING

from fastapi import HTTPException

from ..model import GameStage, PlayerRole
from ..resolver import ActionMixin, GameAction, ModifierType
from .common import RoleDescription, RoleDetails, StageAction
from .teams import Team
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame


general_desc = """
You're the prostitute! You make life complicated for people. 

Every night you choose one person to sleep with. That person gets
no action that night (if they had one). 

Also, you bring them over to your house. If the wolves attack
them, they're not home. But if the wolves attack you, you're both
there...

You win if all the wolves are eliminated. 
"""

description = RoleDescription(
    display_name="You are the prostitute!",
    stages={
        GameStage.NIGHT: StageAction(
            text=f"""
{general_desc}

It's night time now, so choose one person to sleep with. 
""",
            button_text="Sleep with your target",
        ),
        GameStage.DAY: StageAction(text=general_desc),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class AffectedByProstitute(ActionMixin):
    """
    Creates attributes `originator_sleeping_with_prostitute` and
    `target_sleeping_with_prostitute`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originator_sleeping_with_prostitute = False
        self.target_sleeping_with_prostitute = False

        # self.bind_as_modifier(
        #     self.__orig_sleeping,
        #     __class__,
        #     ProstituteAction,
        #     ModifierType.ORIGINATING_FROM_TARGET,
        # )
        # self.bind_as_modifier(
        #     self.__target_sleeping,
        #     __class__,
        #     ProstituteAction,
        #     ModifierType.TARGETTING_TARGET,
        # )

    def __orig_sleeping(self, *args):
        self.originator_sleeping_with_prostitute = True

    def __target_sleeping(self, *args):
        self.target_sleeping_with_prostitute = True


class ProstituteAction(GameAction):
    def execute(self, game):
        # No action required: the prostitute's effect is to modify other actions
        # through the AffectedByProstitute ActionMixin
        pass


def register(role_map):
    role_map.update(
        {
            PlayerRole.PROSTITUTE: RoleDetails(
                role_description=description,
                actions={GameStage.NIGHT: ProstituteAction},
            )
        }
    )
