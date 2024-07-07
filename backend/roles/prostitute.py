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
from ..model import GameStage
from ..model import PlayerRole
from ..resolver import ActionMixin
from ..resolver import GameAction
from ..resolver import GamePlayer
from ..resolver import ModifierType
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .teams import Team
from .utility_mixins import TargetMustBeAlive
from .utility_mixins import TargetMustNotBeSelf
from .villager import description as villager


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
    display_name="You are the Prostitute",
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

    priority = 2

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.bind_as_modifier(
            AffectedByProstitute.__orig_sleeping,
            AffectedByProstitute,
            ProstituteAction,
            ModifierType.ORIGINATING_FROM_TARGET,
        )
        cls.bind_as_modifier(
            AffectedByProstitute.__target_sleeping,
            AffectedByProstitute,
            ProstituteAction,
            ModifierType.TARGETTING_TARGET,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originator_sleeping_with_prostitute = False
        self.target_sleeping_with_prostitute = False

    def __orig_sleeping(self, action: "ProstituteAction"):
        self.originator_sleeping_with_prostitute = True

    def __target_sleeping(self, action: "ProstituteAction"):
        self.target_sleeping_with_prostitute = True


class ProstituteAction(TargetMustBeAlive, TargetMustNotBeSelf, GameAction):
    def do_modifiers(self):
        # Disable any actions originating from the prostitute's target
        for a in self.target.originated_from:
            a.prevented = True

        # Execute the normal modifier search
        super().do_modifiers()


def prostitute_sleeping_with(prostitute: GamePlayer) -> GamePlayer:
    """
    Given a prostitute, return the GamePlayer that they are sleeping with
    """
    if prostitute.model.role != PlayerRole.PROSTITUTE:
        raise TypeError(f"Player {prostitute} is not a prostitute")

    assert len(prostitute.originated_from) == 1

    return prostitute.originated_from[0].target


def register(role_map):
    role_map.update(
        {
            PlayerRole.PROSTITUTE: RoleDetails(
                role_description=description,
                actions={GameStage.NIGHT: ProstituteAction},
            )
        }
    )
