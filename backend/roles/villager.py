"""
The Villager role
"""
from ..model import PlayerRole, GameStage
from .common import RoleDescription, RoleDetails, StageAction


description = RoleDescription(
    display_name="Villager",
    stages={
        GameStage.DAY: StageAction(
            text="""
You are a villager. You have no special powers. Try not to get eaten!

You win if all the wolves are eliminated. 
    """
        ),
        GameStage.NIGHT: StageAction(
            text="""
You have nothing to do at night. Relax...
    """
        ),
        GameStage.VOTING: StageAction(
            text="""
Vote for someone to lynch! Whoever gets the most votes will be killed.

Click someone's icon and click the button. 
    """,
            # button_text="Vote for someone to lynch...",
        ),
    },
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=None,
)


def register(role_map):
    role_map.update({PlayerRole.VILLAGER: RoleDetails(description)})
