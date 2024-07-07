"""
The Mason role

The mason has no special powers, but they have a buddy mason. These two know who each other are.
"""
from typing import TYPE_CHECKING

from ..model import GameStage
from ..model import PlayerRole
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .teams import Team
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame

general_desc = """
You've always had a thing for cults, but you're not into werewolves. Luckily for you, you
know one trustworthy person in this village: your fellow mason. Check the chat to see who
they are.

You don't have any special powers.
You win if all the wolves are eliminated.
"""

description = RoleDescription(
    display_name="You are a Mason",
    stages={
        GameStage.NIGHT: StageAction(
            text=general_desc,
        ),
        GameStage.DAY: StageAction(text=general_desc),
    },
    team=Team.VILLAGERS,
    secret_chat_enabled=RoleDescription.SecretChatType.ROLE,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


def grammatical_join(lst):
    if not lst:
        return ""
    elif len(lst) == 1:
        return str(lst[0])
    return "{} and {}".format(", ".join(lst[:-1]), lst[-1])


def announce_masons(game: "WurwolvesGame"):
    masons = game.get_players_model(role=PlayerRole.MASON)

    for mason in masons:
        other_masons = [p for p in masons if p.id != mason.id]
        other_masons_str = [p.user.name for p in other_masons]

        game.send_chat_message(
            "Your fellow masons are {}".format(grammatical_join(other_masons_str)),
            is_strong=True,
            player_list=[mason.id],
        )


def register(role_map):
    role_map.update(
        {
            PlayerRole.MASON: RoleDetails(
                role_description=description,
                actions={},
                startup_callback=announce_masons,
            )
        }
    )
