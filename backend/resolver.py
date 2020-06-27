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

from .model import ActionModel, GameStage, PlayerModel, PlayerRole, PlayerState

if False:  # for typing
    from ..game import WurwolvesGame


class GamePlayer:
    def __init__(self, player_model: PlayerModel):
        self.model = player_model
        self.originated_from: List[GameAction] = []
        self.targetted_by: List[GameAction] = []


class ActionMixin:
    def __init__(self, *args, **kwargs):
        # End of the line for super() calls: discard all params and stop
        pass

    @staticmethod
    def get_action_method_name(MixinClass, alter_originating: bool):
        return (
            "mod_"
            + MixinClass.__name__
            + ("_originating" if alter_originating else "_targetted")
        )

    def bind_as_modifier(self, func, MixinClass, ActionClass, alter_originating: bool):
        """
        Bind a function from this mixin to the self object using a name generated from the mixin's class

        All instances of ActionClass will now search for actions of MixinClass
        in the do_modifiers() stage. If they find any, they will execute the method func. 

        Specifically, the target of this action will have func called for all the actions
        targetting them if func is available and alter_originating = False. The target of this action
        will have func called for all the actions originating from them if func is available and
        alter_originating = True. 

        Example usage:

            self.bind_as_modifier(self.__do_mod, AffectedByMedic, MedicAction, False)

        This is used to bind dunder methods of a mixin to the parent GameAction with a predictable name

        alter_originating specifices whether the mixin should alter actions which originate from the target 
        or which also target the target. E.g. a Medic wants to alter actions which target the target, whereas
        a Prostitute wants to alter actions which originate from the target. 
        """

        # Make a new class method which calls func
        def new_func(self, func=func):
            func()

        mod_func_name = self.get_action_method_name(MixinClass, alter_originating)
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


class GameAction(ActionMixin):
    # These are lists of mixins that affect child classes of this class, sorted by the child class
    mixins_affecting_originators = {}
    mixins_affecting_targets = {}

    # Override to change the allowed states
    allowed_player_states = [PlayerState.ALIVE]

    # Override to have this action performed once per team, not once per player
    team_action = False

    @classmethod
    def is_action_available(cls, game, stage, stage_id, player_id):
        """
        Is the action enabled at this stage? Override this function if a role needs to prevent
        other actions from even being submitted.

        For example, the Mayor prevents everyone from being able to vote. 
        """
        return True

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
        super().__init__(action_model, players)

    def execute(self, game):
        """Called once all actions have been submitted"""
        raise NotImplementedError

    @classmethod
    def immediate(cls, **kwargs):
        """Called immediately on submit"""
        pass

    def do_modifiers(self):
        """
        Modify actions that relate to the target of this action.

        For each action that either targets or originates from the target of this action, call the
        registered MixinClass actions.
        """
        if self.target:
            # "if I am listed as affecting actions which my target originates..."
            if self.__class__ in GameAction.mixins_affecting_originators:
                # "...loop over the classes of actions which I affect"
                for MixinClass in GameAction.mixins_affecting_originators[
                    self.__class__
                ]:
                    # "For each action that my target originated..."
                    for action in self.target.originated_from:
                        # "...if it is the affected action we're considering..."
                        if isinstance(action, MixinClass):
                            # "...call the 'originator' method to change its behaviour."
                            f = getattr(
                                action,
                                ActionMixin.get_action_method_name(MixinClass, True),
                            )
                            f()
            # Do the same, but for actions which my target is targetted by
            if self.__class__ in GameAction.mixins_affecting_targets:
                for MixinClass in GameAction.mixins_affecting_targets[self.__class__]:
                    for action in self.target.targetted_by:
                        if isinstance(action, MixinClass):
                            f = getattr(
                                action,
                                ActionMixin.get_action_method_name(MixinClass, False),
                            )
                            f()

    @staticmethod
    def get_priority(role: PlayerRole):
        """Get a numerical priority for a given role

        Higher numbers will be higher priority.

        Args:
            role (PlayerRole): The role
        """
        from .roles import get_role_description

        return get_role_description(role).priority


class TargetRequired(ActionMixin):
    def __init__(self, action_model, players):
        if not action_model.selected_player_id:
            raise ValueError(f"{self.__class__} requires a target")
        super().__init__(action_model, players)


class NoTargetRequired(ActionMixin):
    def __init__(self, action_model, players):
        if action_model.selected_player_id:
            raise ValueError(f"{self.__class__} doesn't need a target")
        super().__init__(action_model, players)


def game_ended(game):
    from .roles import team_has_won, win_ends_game, Team, win_action

    wins = [team for team in list(Team) if team_has_won(game, team)]
    for winning_team in wins:
        win_action(game, winning_team)

    game_ending_wins = [w for w in wins if win_ends_game(w)]

    return bool(game_ending_wins)


def judge_night(game: "WurwolvesGame"):
    if game_ended(game):
        game._set_stage(GameStage.ENDED)
    else:
        game._set_stage(GameStage.DAY)
        game.send_chat_message("Day breaks...", is_strong=True)


def switch_to_vote(game: "WurwolvesGame"):
    game._set_stage(GameStage.VOTING)


def count_votes(game: "WurwolvesGame"):
    players: List[PlayerModel] = game.get_players_model()
    votes = [p.votes for p in players]
    voted_player, num_votes = max(zip(players, votes), key=lambda tup: tup[1])

    if votes.count(num_votes) > 1:
        tied = True
        game.send_chat_message("The vote was a tie! Revote...", is_strong=True)
    else:
        tied = False
        game.send_chat_message(f"{voted_player.user.name} got lynched", is_strong=True)
        game.set_player_state(voted_player.id, PlayerState.LYNCHED)

    game.reset_votes()

    if game_ended(game):
        game._set_stage(GameStage.ENDED)
    elif not tied:
        game._set_stage(GameStage.NIGHT)


# Register finalizers for each stages of the game.
# These will have access to an instance of WurwolvesGame and are expected
# to use it to do any actions that are required
# (e.g. changing the game stage, sending game-end chat messages etc)
stage_finalizers = {
    GameStage.NIGHT: judge_night,
    GameStage.DAY: switch_to_vote,
    GameStage.VOTING: count_votes,
}


def process_actions(game: "WurwolvesGame", stage: GameStage, stage_id: int) -> None:
    from .roles import get_role_action

    players = game.get_players_model()
    actions = game.get_actions_model(stage_id)

    game_players = {}
    for p in players:
        game_players[p.id] = GamePlayer(p)

    game_actions = []
    for a in actions:
        action_class = get_role_action(a.player.role, stage)
        game_actions.append(action_class(a, game_players))

    # Sort actions by priority then by action id
    game_actions.sort(key=lambda a: (a.priority, a.model.id))

    # In order, modify all other actions
    for a in game_actions:
        a.do_modifiers()

    # In order, execute the actions
    for a in game_actions:
        logging.info(f"Executing action {a}")
        a.execute(game)

    # Perform any final actions (e.g. changing the game stage) that need to happen
    if stage in stage_finalizers:
        logging.info(f"Stage finalizer registered for {stage}: executing")
        stage_finalizers[stage](game)
    else:
        logging.info(f"No finalizer registered for {stage}")
