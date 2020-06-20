"""
Resolve a game stage

At the end of the night, collate all the Actions stored in the database and
determine what happens.

There are two objects involved in this: GameActions and GamePlayers. 

GamePlayers are constructed from database players. They also have originated_from
or targetted_by fields that contain GameActions which affect that player. 

A GameAction can be constructed from a database action. 

A GameAction may have:
* An originator
* A target
* Modifier methods (named "mod_xxxxxxx")

It must have
* A execute() method

The execute() stage will do the action's work when it is called. This is the
only method which can interact with the game / database. 

The action can be modified by other actions by calling its modifier methods.
These may change the result of the execute stage. The execute stage will always
still be called, but can change its behaviour based on the modifiers that have /
have not been called. 

An Action can discover what Actions are associated with a GamePlayer by looking
at the list of originated_from or targetted_by GameActions on that GamePlayer. 

To resolve the night's actions, the following process will happen:

1. A set of GamePlayers are created, representing all players in the game who
    are not spectating (but including the dead ones, in case we one day want to
    e.g. revive someone)

2. All GameActions are registered. This creates the GameActions with their
    default setup. There is no interactions between GameActions yet: if
    execute() were called, they would all perform their default action. This
    also adds each GameAction to the originated_from and/or targetted_by lists on
    the GamePlayers.

3. All GameActions have their do_modifiers() methods called. These are called in
    priority order, starting with the roles with the highest priority. If a tie
    occurs, resolve the one whose Action was submitted first. 

    This method inspects the originated_from and targetted_by lists of the
    relevant player and calls any modifiers that need to be called. This will
    result in modification of the behaviour of the actions, depending on what
    other actions exist. 

4. All GameActions have their execute() methods called. These perform the
    actions that the GameActions are now configured to do, altering the database
    and sending messages appropriately. 

    It should not matter in which order this occurs since all Actions should now
    be in agreement about what will happen, but it will happen in the same order
    as the modifier application step. 

Example
-------

A game with players: 

Alice : wolf
Bob : villager
Charlie : villager
Dave : medic
Elsa : seer

Step 0

* At night, Alice submits a "kill Charlie" Action. 
* Not all actions are submitted yet, so the night continues
* Elsa submits a "check Alice" action
* Not all actions are submitted yet, so the night continues
* Dave submits a "save Charlie" action
* All actions are submitted, so this module is invoked

Steps 1 & 2

* A GamePlayer is created for each player
* A GameAction is created for each action:
    * the "kill Charlie" GameAction is added to the originated_from list on Alice
        and the targetted_by list on Charles
    * the "check Alice" GameAction is added to the originated_from list on Elsa
        and the targetted_by list on Alice
    * the "save Charlie" GameAction is added to the originated_from list on Dave
        and the targetted_by list on Charlie
* Note that all GameActions are actually subclasses of GameAction, so have other
    modifier methods added

Step 3

* do_modifiers() is called on each GameAction, in priority order:
* "save Charlie" has high priority: it's called first
    * "save Charlie" looks up the "Charlie" GamePlayer by checking its "targets"
        field. 
    * It loops through "Charlie".targetted_by checking for any actions which
        have the "mod_saved_by_medic" method and calls them all
* The "check Alice" GameAction is next:
    * It doesn't need to modify any actions
* The "kill Charlie" GameAction is next:
    * It doesn't need to modify any actions

Step 4

* The execute() steps are called:
* "save Charlie" doesn't need to do anything: it only modifies other actions
* "check Alice" has not been modified, so its default execute() step happens
    * Chat messages are added to the game telling Elsa about Alice
* "Kill Charlie" has been modified by the "modifier_saved_by_medic" modifier
    * It's execute() step therefore does not kill Charlie but might e.g. send a
        message to the wolves

Step 5

* Resolution is completed. All the objects are destroyed (or just forgotted
    about and left to the garbage collector) and the game moves to the next
    stage

"""

import logging
from typing import Dict, List

from .model import ActionModel, GameStage, PlayerModel, PlayerRole

if False:  # for typing
    from ..game import WurwolvesGame


class GamePlayer:
    def __init__(self, player_model: PlayerModel):
        self.model = player_model
        self.originated_from: List[GameAction] = []
        self.targetted_by: List[GameAction] = []


class ActionMixin:
    @staticmethod
    def get_action_method_name(MixinClass):
        return "mod_" + MixinClass.__name__

    def bind_as_modifier(self, func, MixinClass, ActionClass, alter_originating: bool):
        """
        Bind a function from this mixin to the self object using a name generated from the mixin's class

        All instances of ActionClass will now search for actions of MixinClass
        in the do_modifiers() stage. If they find any, they will execute the method func. 

        Example usage:

            self.bind_as_modifier(self.__do_mod, AffectedByMedic, MedicAction, False)

        This is used to bind dunder methods of a mixin to the parent GameAction with a predictable name

        alter_originating specifices whether the mixin should alter action which originate from the target 
        or which also target the target. E.g. a Medic wants to alter actions which target the target, whereas
        a Prostitute wants to alter actions which originate from the target. 
        """

        # Make a new class method which calls func
        def new_func(self):
            func()

        mod_func_name = self.get_action_method_name(MixinClass)
        new_func.__name__ = mod_func_name

        bound_func = new_func.__get__(self, self.__class__)
        setattr(self, mod_func_name, bound_func)

        # Register the MixinClass as a modifier of targets for this ActionClass
        if alter_originating:
            if ActionClass not in GameAction.mixins_affecting_originators:
                GameAction.mixins_affecting_originators[ActionClass] = []
            GameAction.mixins_affecting_originators[ActionClass].append(MixinClass)
        else:
            if ActionClass not in GameAction.mixins_affecting_targets:
                GameAction.mixins_affecting_targets[ActionClass] = []
            GameAction.mixins_affecting_targets[ActionClass].append(MixinClass)


class GameAction:
    # These are lists of mixins that affect child classes of this class, sorted by the child class
    mixins_affecting_originators = {}
    mixins_affecting_targets = {}

    def __init__(self, action_model: ActionModel, players: Dict[int, GamePlayer]):
        self.model: ActionModel = action_model
        self.originator: GamePlayer = None
        self.target: GamePlayer = None

        # Get the originator
        self.originator = players[action_model.player_id]

        # If there's a target, get it too
        if action_model.selected_player_id:
            self.target = players[action_model.selected_player_id]

        self.priority = GameAction.get_priority(self.model.player.role)

        # Add this object to the target and originator's lists
        self.originator.originated_from.append(self)
        if self.target:
            self.target.targetted_by.append(self)

        # Init any mixins registered
        super().__init__()

    def execute(self, game):
        """Called once all actions have been submitted"""
        raise NotImplementedError

    @classmethod
    def immediate(cls, game):
        """Called immediatly on submit"""
        pass

    def do_modifiers(self):
        # TODO: check this logic, I don't think it's right
        if self.target:
            if self.__class__ in GameAction.mixins_affecting_originators:
                for MixinClass in GameAction.mixins_affecting_originators[
                    self.__class__
                ]:
                    for action in self.target.originated_from:
                        if isinstance(action, MixinClass):
                            f = getattr(
                                action, ActionMixin.get_action_method_name(MixinClass)
                            )
                            f()
            if self.__class__ in GameAction.mixins_affecting_targets:
                for MixinClass in GameAction.mixins_affecting_targets[self.__class__]:
                    for action in self.target.targetted_by:
                        if isinstance(action, MixinClass):
                            f = getattr(
                                action, ActionMixin.get_action_method_name(MixinClass)
                            )
                            f()

    @staticmethod
    def get_priority(role: PlayerRole):
        """Get a numerical priority for a given role

        Higher numbers will be higher priority.

        Args:
            role (PlayerRole): The role
        """
        from .roles import ROLE_MAP

        return ROLE_MAP[role].role_description.priority


def process_actions(game: "WurwolvesGame") -> GameStage:
    from .roles import ROLE_MAP

    stage = game.get_game_model().stage
    players = game.get_players_model()
    actions = game.get_actions_model()

    game_players = {}
    for p in players:
        game_players[p.id] = GamePlayer(p)

    game_actions = []
    for a in actions:
        action_class = ROLE_MAP[a.player.role].actions[stage]
        game_actions.append(action_class(a, game_players))

    # Sort actions by priority then by action id
    game_actions.sort(key=lambda a: (a.priority, a.model.id))

    # In order, modify all other actions
    for a in game_actions:
        a.do_modifiers()

    # In order, execute the actions
    for a in game_actions:
        a.execute(game)

    logging.warning("process_actions just returning same stage: not coded yet")
    return stage
