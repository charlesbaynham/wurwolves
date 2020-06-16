'''
The Seer role
'''
import logging

from ..model import PlayerRole
from ..resolver import GameAction
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails
from .wolf import AffectedByWolves

if False:  # for typing
    from ..game import WurwolvesGame

description = RoleDescription(
    display_name="Seer",
    night_action=True,
    night_button_text="Select someone to check",
    day_text="""
You are a Seer! You get to check the identity of one person each night. 

You win if all the wolves are eliminated. 
    """,
    night_text="""
Choose who to check...
    """,
    vote_text=None,
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=DEFAULT_ROLE,
)


class SeerAction(GameAction, AffectedByWolves):
    def execute(self, game: 'WurwolvesGame'):
        from .registration import get_role_team

        seer_name = self.originator.model.user.name
        target_name = self.target.model.user.name
        target_is_wolf = get_role_team(self.target.model.role) == RoleDescription.Team.WOLVES

        logging.info(f"Seer: {seer_name} checks {target_name}")

        if self.originator_attacked_by_wolf:
            game.send_chat_message(
                f"You checked {target_name} but were rudely interrupted",
                is_strong=False,
                player_list=[self.originator.model.id]
            )
        elif target_is_wolf:
            game.send_chat_message(
                f"You checked {target_name}... they are a wolf!",
                is_strong=True,
                player_list=[self.originator.model.id]
            )
        else:
            game.send_chat_message(
                f"You checked {target_name}... they are not a wolf",
                is_strong=False,
                player_list=[self.originator.model.id]
            )


def register(role_map):
    role_map.update({
        PlayerRole.SEER: RoleDetails(description, SeerAction)
    })
