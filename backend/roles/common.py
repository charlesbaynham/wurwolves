from enum import Enum
from typing import NamedTuple, Union

import pydantic

from ..resolver import GameAction


class RoleDescription(pydantic.BaseModel):
    display_name: str

    night_action: bool
    night_action_url: Union[None, str] = None
    night_action_select_person = True
    night_button_text: Union[None, str] = None
    vote_button_text: Union[None, str] = None

    day_text: Union[None, str] = None
    night_text: Union[None, str] = None
    vote_text: Union[None, str] = None

    priority: int = 0

    class Team(Enum):
        VILLAGERS = 'VILLAGERS'
        WOLVES = 'WOLVES'
        SPECTATORS = 'SPECTATORS'
    team: Team

    fallback_role: Union[None, "RoleDescription"]

    class Config:
        allow_mutation = False


RoleDescription.update_forward_refs()


class RoleDetails(NamedTuple):
    '''
    A RoleDetails tuple contains a complete description of what a role entails
    It can be used to figure out how a role should behave and will be stored in
    .registration.ROLE_MAP
    '''
    role_description: RoleDescription
    role_action: GameAction


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
    vote_button_text="Vote for someone to lynch...",
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=None,
)


class ActionMixin():
    @staticmethod
    def get_action_method_name(MixinClass):
        return "mod_" + MixinClass.__name__

    def bind_as_modifier(self, func, MixinClass, ActionClass, alter_originating: bool):
        '''
        Bind a function from this mixin to the self object using a name generated from the mixin's class

        All instances of ActionClass will now search for actions of MixinClass
        in the do_modifiers() stage. If they find any, they will execute the method func. 

        This is used to bind dunder methods of a mixin to the parent GameAction with a predictable name

        alter_originating specifices whether the mixin should alter action which originate from the target 
        or which also target the target. E.g. a Medic wants to alter actions which target the target, whereas
        a Prostitute wants to alter actions which originate from the target. 
        '''

        # Make a new class method which calls func
        def new_func(self):
            func()

        mod_func_name = self.get_action_method_name(MixinClass)
        new_func.__name__ = mod_func_name

        bound_func = new_func.__get__(self, self.__class__)
        setattr(self, mod_func_name, bound_func)

        # Register the MixinClass as a modifier of targets for the ActionClass
        if alter_originating:
            ActionClass.mixins_affecting_originators.append(MixinClass)
        else:
            ActionClass.mixins_affecting_targets.append(MixinClass)
