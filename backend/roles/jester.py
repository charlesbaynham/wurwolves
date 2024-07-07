"""
The Jester role

The jester wins by getting themselves lynched by the villagers
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

general_text = """
You win if you get yourself lynched by the villagers. The wolves know who
you are and shouldn't kill you, since you'll confuse the villagers which
helps the wolves. They can if they want to though, so don't annoy them...

"""

description = RoleDescription(
    display_name="You are the Jester!",
    stages={
        GameStage.DAY: StageAction(text=general_text),
        GameStage.NIGHT: StageAction(
            text=f"""
{general_text}

You have nothing to do at night. Plot your jesting.
    """
        ),
    },
    team=Team.JESTER,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


def announce_to_wolves(game: "WurwolvesGame"):
    jester = game.get_players_model(role=PlayerRole.JESTER)

    if jester:
        if len(jester) > 1:
            raise TypeError("More than one jester! Not programmed for this...")

        jester = jester[0]
        wolves = game.get_players_model(role=PlayerRole.WOLF)

        game.send_chat_message(
            "There's a jester in the game: it's {}".format(jester.user.name),
            is_strong=True,
            player_list=[p.id for p in wolves],
        )


def register(role_map):
    role_map.update(
        {
            PlayerRole.JESTER: RoleDetails(
                role_description=description, startup_callback=announce_to_wolves
            )
        },
    )
