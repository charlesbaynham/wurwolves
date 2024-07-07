"""
The Miller role

The Miller can't do shit, and if the seer checks them they look like a wolf
"""
from ..model import GameStage
from ..model import PlayerRole
from ..resolver import GameAction
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .teams import Team
from .villager import description as villager


general_desc = """
Oh dear, you're the miller.

You don't have any special powers, but if the seer checks you then you'll look like a wolf. Good luck!

You win if all the wolves are eliminated.
"""

description = RoleDescription(
    display_name="You are the Miller...",
    stages={
        GameStage.NIGHT: StageAction(
            text=general_desc,
        ),
        GameStage.DAY: StageAction(text=general_desc),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class ConfusedByMiller(GameAction):
    """
    Creates attribute `target_is_miller`

    No need to use bind_as_modifier since this mixin doesn't care about what
    other actions target / originate from the targetted player, it only cares
    about their role.
    """

    @property
    def target_is_miller(self):
        return self.target.model.role == PlayerRole.MILLER


def register(role_map):
    role_map.update(
        {PlayerRole.MILLER: RoleDetails(role_description=description, actions={})}
    )
