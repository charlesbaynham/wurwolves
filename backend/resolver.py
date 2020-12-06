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
    priority order, starting with the actions with the highest priority. If a tie
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
from enum import Enum
from typing import Dict
from typing import List

from .model import ActionModel
from .model import GameStage
from .model import PlayerModel
from .model import PlayerState

if False:  # for typing
    from ..game import WurwolvesGame


class GamePlayer:
    def __init__(self, player_model: PlayerModel):
        self.model = player_model
        self.originated_from: List[GameAction] = []
        self.targetted_by: List[GameAction] = []


class ModifierType(Enum):
    TARGETTING_TARGET = "TARGETTING_TARGET"
    ORIGINATING_FROM_TARGET = "ORIGINATING_FROM_TARGET"
    TARGETTING_ORIGINATOR = "TARGETTING_ORIGINATOR"
    ORIGINATING_FROM_ORIGINATOR = "ORIGINATING_FROM_ORIGINATOR"


class ActionMixin:
    def __init__(self, *args, **kwargs):
        # End of the line for super() calls: discard all params and stop
        pass

    @staticmethod
    def get_action_method_name(MixinClass, modifier_type: ModifierType):
        return f"mod_{MixinClass.__name__}_{modifier_type.value}"

    @classmethod
    def bind_as_modifier(
        cls, func, MixinClass, ActionClass, modifier_type: ModifierType
    ):
        """
        Bind a function from this mixin to this class using a name generated from the mixin's class

        All instances of ActionClass will now search for actions of MixinClass
        in the do_modifiers() stage. If they find any, they will execute the method func.
        ``modifier_type`` specifies where they search.

        For example, the target of this action will have func called for all the actions
        targetting them if func is available and ``modifier_type`` = TARGETTING_TARGET.

        The originator of this action will have func called for all the actions targetting
        from them if func is available and ``modifier_type`` = TARGETTING_ORIGINATOR.

        Example usage:

            AffectedByMedic.bind_as_modifier(self.__do_mod, AffectedByMedic, MedicAction, TARGETTING_ORIGINATOR)

        This can be used to bind dunder methods of a mixin to the parent GameAction with a predictable name.
        It should probably be called when setting up the modified classes, e.g. in __init_subclass__ of the
        action mixin. The bound function (__do_mod) must accept the action which triggered the call as an
        argument.

        ``modifier_type`` specifices which actions should be searched for the registered method.
        E.g. a Medic wants to alter actions which target the target, whereas a Prostitute
        wants to alter actions which originate from the target.
        """

        mod_func_name = cls.get_action_method_name(MixinClass, modifier_type)
        setattr(cls, mod_func_name, func)

        # Register the MixinClass as a modifier of targets for this ActionClass
        mixin_dict = GameAction.mixins_registered[modifier_type]
        if ActionClass not in mixin_dict:
            mixin_dict[ActionClass] = []
        mixin_dict[ActionClass].append(MixinClass)


class RoundEndBehaviour(Enum):
    ONCE_REQUIRED = 1
    ONCE_OPTIONAL = 2
    MULTIPLE_OPTIONAL = 3


class TeamBehaviour(Enum):
    # Each player can submit this action independently
    ONCE_PER_PLAYER = 1

    # The first player to submit this action is the only player on their team allowed to
    ONCE_PER_TEAM = 2

    # The first player to submit, chooses on behalf of every player on their team.
    # The action is duplicated and assigned to all their team mates
    DUPLICATED_PER_ROLE = 3


class GameAction(ActionMixin):
    # This is a dict of mixins which affect child classes of this class. There is one entry for each
    # type of interaction, i.e. each ModifierType. Each ModifierType has a dict of child class -> mixins
    # which affect it.
    # This dict gets populated by bind_as_modifier.
    mixins_registered = {
        ModifierType.ORIGINATING_FROM_ORIGINATOR: {},
        ModifierType.ORIGINATING_FROM_TARGET: {},
        ModifierType.TARGETTING_TARGET: {},
        ModifierType.TARGETTING_ORIGINATOR: {},
    }

    # Override to change the allowed states
    allowed_player_states = [PlayerState.ALIVE]

    # Override to have this action performed once per team, not once per player
    team_action = TeamBehaviour.ONCE_PER_PLAYER

    # Override to change how this action does / doesn't hold up the round end
    round_end_behaviour = RoundEndBehaviour.ONCE_REQUIRED

    # Is this action only available to active players? I.e. ones who have been
    # seen recently. For example, we want the game to wait until the seer has
    # selected someone even if they've logged off for a bit, but we don't want
    # the game to wait for inactive spectators to return when we're voting to
    # start a new game
    active_players_only = False

    # The priority of this action determine which actions execute first. Higher numbers
    # are higher priority
    priority = 0

    @classmethod
    def is_action_available(cls, game, stage, stage_id, player_id):
        """
        Is the action enabled at this stage? Override this function if a role needs to prevent
        other actions from even being submitted.

        For example, the Mayor prevents everyone from being able to vote.
        """
        logging.debug("Default is_action_available used")
        return True

    def __init__(self, action_model: ActionModel, players: Dict[int, GamePlayer]):
        self.model: ActionModel = action_model
        self.originator: GamePlayer = None
        self.target: GamePlayer = None
        self.prevented = False

        # Get the originator
        self.originator = players[action_model.player_id]

        # If there's a target, get it too
        if action_model.selected_player_id:
            self.target = players[action_model.selected_player_id]

        # Add this object to the target and originator's lists
        self.originator.originated_from.append(self)
        if self.target:
            self.target.targetted_by.append(self)

        # Init any mixins registered
        super().__init__(action_model, players)

    def execute(self, game):
        """
        Called once all actions have been submitted

        This method should respect the state of self.prevented
        """
        pass

    @classmethod
    def immediate(cls, **kwargs):
        """
        Called immediately on submit

        If this method returns False, the storage of the action will be aborted. Note
        that this must actually be "false", not just a falsy value.
        """
        return True

    def do_modifiers(self):
        """
        Modify actions that relate to the target of this action.

        For each action that either targets or originates from the target of this action, call the
        registered MixinClass actions.
        """

        # This code kept for reference. This is what the resolution looks like for a single
        # modifier type: ORIGINATING_FROM_TARGET. Note that it's the same for all modifier
        # types, except for the "for action in self.target.originated_from" bit.
        # This is the bit that the code breaks out so that the four modifier types can be
        # done otherwise identically.

        # # Get the dict of actions which alter actions originating from their target
        # dict_of_affected_actions = GameAction.mixins_registered[
        #     ModifierType.ORIGINATING_FROM_TARGET
        # ]
        # # "if I am listed as affecting actions which my target originates..."
        # if self.__class__ in dict_of_affected_actions:
        #     # "...loop over the classes of actions which I affect"
        #     for MixinClass in dict_of_affected_actions[self.__class__]:
        #         # "For each action that my target originated..."
        #         for action in self.target.originated_from:
        #             # "...if it is the affected action we're considering..."
        #             if isinstance(action, MixinClass):
        #                 # "...call the 'originator' method to change its behaviour."
        #                 f = getattr(
        #                     action,
        #                     ActionMixin.get_action_method_name(
        #                         MixinClass, ModifierType.ORIGINATING_FROM_TARGET
        #                     ),
        #                 )
        #                 f()

        # Make a map of "given an action, get the list of relevant actions for each ModifierType"
        action_map = {
            ModifierType.ORIGINATING_FROM_TARGET: lambda a: a.target.originated_from,
            ModifierType.TARGETTING_TARGET: lambda a: a.target.targetted_by,
            ModifierType.ORIGINATING_FROM_ORIGINATOR: lambda a: a.originator.originated_from,
            ModifierType.TARGETTING_ORIGINATOR: lambda a: a.originator.targetted_by,
        }

        for modifier_type in list(ModifierType):
            # Get the dict of actions of this type
            dict_of_affected_actions = GameAction.mixins_registered[modifier_type]

            # "if I am listed as affecting actions according to this ModifierType..."
            if self.__class__ in dict_of_affected_actions:
                # "...loop over the classes of actions which I affect"
                for MixinClass in dict_of_affected_actions[self.__class__]:
                    # Get the list of relevant actions
                    relevant_actions = action_map[modifier_type](self)
                    # "For each action in the relevant list of actions, according to the ModifierType..."
                    for action in relevant_actions:
                        # "...if it is the affected action we're considering..."
                        if isinstance(action, MixinClass):
                            # "...call the registered method to change its behaviour."
                            f = getattr(
                                action,
                                ActionMixin.get_action_method_name(
                                    MixinClass, modifier_type
                                ),
                            )
                            f(self)

    @classmethod
    def get_priority(cls):
        """Get a numerical priority for this role

        Higher numbers will be higher priority.
        """
        return cls.priority


def game_ended(game):
    from .roles import team_has_won, win_ends_game, Team, win_action

    wins = [team for team in list(Team) if team_has_won(game, team)]
    for winning_team in wins:
        win_action(game, winning_team)

    game_ending_wins = [w for w in wins if win_ends_game(w)]

    return bool(game_ending_wins)


def judge_night(game: "WurwolvesGame"):
    if game_ended(game):
        game.end_game()
    else:
        game._set_stage(GameStage.DAY)
        game.send_chat_message("Day breaks...", is_strong=False)


def switch_to_vote(game: "WurwolvesGame"):
    game._set_stage(GameStage.VOTING)


def start_game(game: "WurwolvesGame"):
    game.start_game()


def count_votes(game: "WurwolvesGame"):
    players: List[PlayerModel] = game.get_players_model()
    votes = [p.votes for p in players]
    voted_player, num_votes = max(zip(players, votes), key=lambda tup: tup[1])

    tied = votes.count(num_votes) > 1
    end_vote = True

    if tied:
        if game.num_attempts_this_stage == 0:
            game.send_chat_message("The vote was a tie! Revote...", is_strong=True)
            game.reset_votes()
            game.num_attempts_this_stage = 1
            end_vote = False
        else:
            game.send_chat_message(
                "The vote was a tie again! No one gets lynched.", is_strong=True
            )

    else:
        game.send_chat_message(f"{voted_player.user.name} got lynched", is_strong=True)
        game.kill_player(voted_player.id, PlayerState.LYNCHED)
        game.reset_votes()

    if game_ended(game):
        game.end_game()
    elif end_vote:
        game._set_stage(GameStage.NIGHT)


# Register finalizers for each stages of the game.
# These will have access to an instance of WurwolvesGame and are expected
# to use it to do any actions that are required
# (e.g. changing the game stage, sending game-end chat messages etc)
stage_finalizers = {
    GameStage.NIGHT: judge_night,
    GameStage.DAY: switch_to_vote,
    GameStage.VOTING: count_votes,
    GameStage.ENDED: start_game,
    GameStage.LOBBY: start_game,
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
