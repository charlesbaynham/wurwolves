"""
The Wolf role
"""
from ..model import GameStage
from ..model import PlayerRole
from ..model import PlayerState
from ..resolver import GameAction
from ..resolver import ModifierType
from ..resolver import TeamBehaviour
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .medic import AffectedByMedic
from .medic import is_saved_by_medic
from .prostitute import AffectedByProstitute
from .prostitute import prostitute_sleeping_with
from .teams import Team
from .utility_mixins import TargetMustBeAlive
from .utility_mixins import TargetRequired
from .villager import description as villager

description = RoleDescription(
    display_name="You are a Wolf!",
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
    secret_chat_enabled=RoleDescription.SecretChatType.TEAM,
    reveal_others_text="fellow wolves",
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


def announce_wolves(game: "WurwolvesGame"):
    num_wolves = len(game.get_players(role=PlayerRole.WOLF))

    if num_wolves == 1:
        msg = f"There is only one wolf in the game"
    else:
        msg = f"There are {num_wolves} wolves in the game"

    game.send_chat_message(
        msg,
        is_strong=False,
    )


class AffectedByWolves(AffectedByMedic):
    """
    Creates attributes `originator_attacked_by_wolf` and `target_attacked_by_wolf`.
    These can be cancelled by medic action
    """

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.bind_as_modifier(
            AffectedByWolves.__orig_attacked,
            AffectedByWolves,
            WolfAction,
            ModifierType.ORIGINATING_FROM_TARGET,
        )

        cls.bind_as_modifier(
            AffectedByWolves.__target_attacked,
            AffectedByWolves,
            WolfAction,
            ModifierType.TARGETTING_TARGET,
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


class WolfAction(
    TargetMustBeAlive, TargetRequired, AffectedByMedic, AffectedByProstitute, GameAction
):

    # Any wolf kill counts as the kill for all the wolves
    team_action = TeamBehaviour.DUPLICATED_PER_ROLE

    @classmethod
    def immediate(cls, game=None, user_id=None, selected_id=None, **kw):
        super().immediate(game=game, user_id=user_id, selected_id=selected_id, **kw)
        originator = game.get_user_name(user_id)
        attacked = game.get_user_name(selected_id)
        game.send_team_message(
            user_id, f"(wolves) {originator} has attacked {attacked}"
        )

    def execute(self, game):
        kills = [self.target]

        if self.prevented or self.target_sleeping_with_prostitute:
            return

        if self.target.model.role == PlayerRole.PROSTITUTE:
            kills.append(prostitute_sleeping_with(self.target))

        for kill in kills:
            if not is_saved_by_medic(kill) and kill.model.state == PlayerState.ALIVE:
                target_name = kill.model.user.name
                game.send_chat_message(
                    f"{target_name} was brutally murdered", is_strong=True
                )
                # Be sure to keep the model in-sync with the database, since later
                # actions might read it
                kill.model.state = PlayerState.WOLFED
                game.kill_player(kill.model.id, PlayerState.WOLFED)


def register(role_map):
    role_map.update(
        {
            PlayerRole.WOLF: RoleDetails(
                role_description=description,
                actions={GameStage.NIGHT: WolfAction},
                startup_callback=announce_wolves,
            )
        }
    )
