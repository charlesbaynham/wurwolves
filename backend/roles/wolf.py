"""
The Wolf role
"""

from ..model import GameStage, PlayerRole, PlayerState
from ..resolver import GameAction, ModifierType
from .common import RoleDescription, RoleDetails, StageAction
from .medic import AffectedByMedic
from .teams import Team
from .utility_mixins import TargetRequired
from .villager import description as villager

description = RoleDescription(
    display_name="Wolf",
    stages={
        GameStage.DAY: StageAction(
            text="""
You are a Wolf! You kill one person each night

You win if the wolves kill enough villagers that you are equal in number

You have access to secret chat: use it to chat with the other wolves (if there are any).
    """
        ),
        GameStage.NIGHT: StageAction(
            text="""
You are a Wolf! You kill one person each night

It's night now, so choose whom to kill! Click their icon then click the button to submit. 

You have access to secret chat: use it to chat with the other wolves (if there are any) and decide who to kill.
    """,
            button_text="Select someone to maul",
        ),
    },
    team=Team.WOLVES,
    secret_chat_enabled=True,
    reveal_others_text="fellow wolves",
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class AffectedByWolves(AffectedByMedic):
    """
    Creates attributes `originator_attacked_by_wolf` and `target_attacked_by_wolf`. 
    These can be cancelled by medic action
    """

    def __init_subclass__(cls):
        cls.bind_as_modifier(
            cls.__orig_attacked, cls, WolfAction, ModifierType.ORIGINATING_FROM_TARGET,
        )

        cls.bind_as_modifier(
            cls.__target_attacked, cls, WolfAction, ModifierType.TARGETTING_TARGET,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originator_attacked_by_wolf = False
        self.target_attacked_by_wolf = False

    def __orig_attacked(self, *args):
        if not self.originator_saved_by_medic:
            self.originator_attacked_by_wolf = True

    def __target_attacked(self, *args):
        if not self.target_saved_by_medic:
            self.target_attacked_by_wolf = True


class WolfAction(GameAction, AffectedByMedic, TargetRequired):

    # Any wolf kill counts as the kill for all the wolves
    team_action = True

    @classmethod
    def immediate(cls, game=None, user_id=None, selected_id=None, **kw):
        originator = game.get_user_name(user_id)
        attacked = game.get_user_name(selected_id)
        game.send_team_message(
            user_id, f"(wolves) {originator} has attacked {attacked}"
        )

    def execute(self, game):
        target_name = self.target.model.user.name

        if not self.target_saved_by_medic:
            game.send_chat_message(
                f"{target_name} was brutally murdered", is_strong=True
            )
            game.kill_player(self.target.model.id, PlayerState.WOLFED)


def register(role_map):
    role_map.update(
        {
            PlayerRole.WOLF: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: WolfAction}
            )
        }
    )
