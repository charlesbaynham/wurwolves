import pydantic
from typing import Union
from .model import PlayerRole


class RoleDescription(pydantic.BaseModel):
    display_name: str

    night_action: bool
    night_action_url: Union[None, str] = None
    night_action_select_person = True
    night_button_text: Union[None, str] = None

    day_text: Union[None, str] = None
    night_text: Union[None, str] = None
    vote_text: Union[None, str] = None

    fallback_role: Union[None, "RoleDescription"]


DEFAULT_ROLE = RoleDescription(
    display_name="Villager",
    night_action=False,
    day_text="""
You are a villager. You have no special powers. Try not to get eaten!

You win if all the wolves are eliminated. 
    """,
    night_text="""
You have nothing to do at night. Relax...
    """,
    vote_text="""
Vote for someone to lynch! Whoever gets the most votes will be killed.

Click someone's icon and click the button. 
    """,
    fallback_role=None,
)


ROLE_MAP = {
    PlayerRole.VILLAGER: DEFAULT_ROLE,
    PlayerRole.SEER: DEFAULT_ROLE,
    PlayerRole.MEDIC: DEFAULT_ROLE,
    PlayerRole.WOLF: DEFAULT_ROLE,
    PlayerRole.SPECTATOR: DEFAULT_ROLE,
}
