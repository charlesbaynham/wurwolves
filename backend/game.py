"""
Game module

This module provides the WurwolvesGame class, for interacting with a single game
"""
import asyncio
import datetime
import logging
import os
import random
import time
from functools import wraps
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

import pydantic
from fastapi import HTTPException
from sqlalchemy import bindparam
from sqlalchemy import or_
from sqlalchemy.ext import baked

from . import resolver
from . import roles
from .model import Action
from .model import ActionModel
from .model import DistributionSettings
from .model import FrontendState
from .model import Game
from .model import GameModel
from .model import GameStage
from .model import hash_game_tag
from .model import Message
from .model import Player
from .model import PlayerModel
from .model import PlayerRole
from .model import PlayerState
from .model import User
from .model import UserModel
from .roles import get_action_func_name
from .roles import get_apparant_role


SPECTATOR_TIMEOUT = datetime.timedelta(seconds=40)

# Time for get_hash to wait for until it returns. Clients will have their
# queries held open for this time, unless an update occurs
GET_HASH_TIMEOUT = 20

MAX_NAME_LENGTH = 25

NAMES_FILE = os.path.join(os.path.dirname(__file__), "names.txt")
names = None

update_events: Dict[int, asyncio.Event] = {}

logger = logging.getLogger("game")

# A bakery for SQLAlchemy queries
bakery = baked.bakery()


# Presets for role generation
LOOKUP_CONFIG = {
    "easy": DistributionSettings(
        role_weights={
            # No roles: essential ones only
        }
    ),
    "medium": DistributionSettings(
        role_weights={
            PlayerRole.JESTER: 1,
            PlayerRole.VIGILANTE: 1,
            PlayerRole.MAYOR: 1,
            PlayerRole.MILLER: 1,
        }
    ),
    "hard": DistributionSettings(),  # Default setting: all roles
}


class ChatMessage(pydantic.BaseModel):
    text: str
    is_strong = False


class WurwolvesGame:
    """
    Provides methods for accessing all the properties of a wurwolves game. This
    object is initialized with the ID of a game and loads all other information
    from the database on request.
    """

    def __init__(self, game_tag: str, session=None):
        """Make a new WurwolvesGame for controlling / getting information about a game

        Arguments:
        game_tag (str): Tag of the game. This will be hashed to become the database id
        """
        self.game_id = hash_game_tag(game_tag)
        self._session = session
        self._session_users = 0
        self._session_is_external = bool(session)
        self._db_scoped_altering = False

    @classmethod
    def from_id(cls, game_id: int, **kwargs) -> "WurwolvesGame":
        """
        Make a WurwolvesGame from a game ID instead of a tag
        """
        g = WurwolvesGame("", **kwargs)
        g.game_id = game_id
        return g

    def _check_for_dirty_session(self):
        if self._session.dirty or self._session.new or self._session.deleted:
            self._session_modified = True
            logger.debug("Marking changes as present")

    def db_scoped(func: Callable):
        """
        Start a session and store it in self._session

        When a @db_scoped method returns, commit the session

        Close the session once all @db_scoped methods are finished (if the session is not external)

        If any of the decorated functions altered the database state, also release an asyncio
        event marking this game as having been updated
        """
        from . import database

        @wraps(func)
        def f(self, *args, **kwargs):

            if not self._session:
                self._session = database.Session()
            if self._session_users == 0:
                self._session_modified = False

            try:
                self._session_users += 1
                out = func(self, *args, **kwargs)

                # If this commit will alter the database, set the modified flag
                self._check_for_dirty_session()

                return out
            except Exception as e:
                logging.exception("Exception encountered! Rolling back DB")
                self._session.rollback()
                raise e
            finally:
                if self._session_users == 1 and self._session_modified:
                    # If any of the functions altered the game state, fire
                    # the corresponding updates events if they are present
                    # in the global dict And mark the game as altered in the
                    # database.
                    #
                    # Check this before we reduce session_users to 0, else
                    # calling get_game will reopen a new session before the
                    # old one is closed.
                    logger.debug("Touching game")
                    g = self.get_game()
                    g.touch()

                self._session_users -= 1

                if self._session_users == 0:
                    logger.debug("Committing session")
                    self._session.commit()

                    if self._session_modified:
                        logger.debug("...and triggering updates")
                        trigger_update_event(self.game_id)

        return f

    @db_scoped
    def join(self, user_id: UUID):
        """Join or rejoin a game as a user

        Args:
            user_ID (str): ID of the user
        """
        logger.info("User %s joining now" % user_id)

        # Get the user from the user list, adding them if not already present
        user = self.get_user(user_id)
        if not user:
            logger.info("User %s not in DB" % user_id)
            user = self.make_user(self._session, user_id)

        # Get the game, creating it if it doesn't exist
        game = self.get_game()
        if not game:
            game = self.create_game()
            self.send_chat_message(f"New game created by {user.name}")

        # Add this user to the game as a spectator if they're not already in it
        player = self.get_player(user_id, filter_by_activity=False)

        if not player:
            player = Player(
                role=PlayerRole.SPECTATOR,
                state=PlayerState.SPECTATING,
            )

            logger.info(
                "Adding user %s to game %s with ID %s", user_id, self.game_id, player.id
            )

            game.players.append(player)
            user.player_roles.append(player)
            self.touch()

        if not player.active:
            player.active = True

        # To avoid instant kicking:
        self.player_keepalive(user_id)

        logger.debug("User %s join complete" % user_id)

    @staticmethod
    def make_user(session, user_id) -> User:
        """
        Make a new user

        Note that, since this is a static method, it has no access to self._session and
        so must be passed a session to use.
        """
        logger.debug("make_user start")

        user = User(
            id=user_id,
            name=WurwolvesGame.generate_name(),
            name_is_generated=True,
        )
        session.add(user)

        logger.info("Making new user {} = {}".format(user.id, user.name))
        logger.debug("make_user end")

        return user

    @db_scoped
    def get_game(self) -> Game:
        baked_query = bakery(lambda session: session.query(Game))
        baked_query += lambda q: q.filter(Game.id == bindparam("game_id"))

        result = baked_query(self._session).params(game_id=self.game_id).first()

        return result

    @db_scoped
    def get_game_model(self) -> GameModel:
        g = self.get_game()
        return GameModel.from_orm(g) if g else None

    @db_scoped
    def get_player_id(self, user_id: UUID) -> int:
        game = self.get_game()

        for p in game.players:
            if p.user_id == user_id:
                return p.id

        raise KeyError(f"User {user_id} not found in this game")

    @db_scoped
    def get_player(self, user_id: UUID, filter_by_activity=True) -> Player:
        """
        Get a Player database model for this Game based on the User's UUID. If
        `filter_by_activity`, only return players who should be displayed in this
        stage of the game.
        """
        players = self.get_players(filter_by_activity=filter_by_activity)

        this_player = [p for p in players if p.user_id == user_id]

        if this_player:
            return this_player[0]
        else:
            return None

    @db_scoped
    def get_player_by_id(self, player_id: int, filter_by_activity=False) -> Player:
        """
        Get a Player database model based on the Player's ID. If
        `filter_by_activity`, only return Players who should be displayed in this
        stage of the game.
        """

        p = self._session.query(Player).get(player_id)

        if filter_by_activity and not _player_is_active(p):
            return None

        return p

    @db_scoped
    def get_player_model(self, user_id: UUID) -> PlayerModel:
        p = self.get_player(user_id)
        return PlayerModel.from_orm(p) if p else None

    @db_scoped
    def get_player_model_by_id(self, player_id: int) -> PlayerModel:
        p = self.get_player_by_id(player_id)
        return PlayerModel.from_orm(p) if p else None

    @db_scoped
    def get_players(
        self, role: PlayerRole = None, filter_by_activity=True
    ) -> List[Player]:
        """
        Get all Players in this Game

        If `filter_by_activity`, only return Players who should be displayed in
        this stage of the game.
        """
        game = self.get_game()
        if not game:
            raise HTTPException(404, "Game not found")

        players = game.players

        if filter_by_activity:
            players = [p for p in players if _player_is_active(p)]

        if role:
            players = [p for p in players if p.role == role]

        return players

    @db_scoped
    def get_players_model(self, role: PlayerRole = None) -> List[PlayerModel]:
        return [PlayerModel.from_orm(p) for p in self.get_players(role)]

    @db_scoped
    def get_actions(
        self,
        stage_id=None,
        player_id: int = None,
        stage: GameStage = None,
        include_expired=False,
    ) -> List[Action]:
        """Get orm objects for Actions in this game.

        Filter by the passed parameters if any.
        """
        actions = self.get_game().actions

        if stage_id:
            actions = [a for a in actions if a.stage_id == stage_id]

        if player_id:
            actions = [a for a in actions if a.player_id == player_id]

        if stage:
            actions = [a for a in actions if a.stage == stage]

        if not include_expired:
            actions = [a for a in actions if a.expired == False]

        return actions

    @db_scoped
    def get_actions_model(
        self, stage_id=None, player_id: int = None, stage: GameStage = None
    ) -> List[ActionModel]:
        """Get models for Actions in this game.

        Filter by the passed parameters if any.

        Default to the current stage."""
        return [
            ActionModel.from_orm(a)
            for a in self.get_actions(stage_id, player_id, stage)
        ]

    @db_scoped
    def num_previous_stages(self, stage_type: GameStage, stage_id=None):
        """
        Number of stages of the given type which have occured prior to this one, identified by stage_id.
        If stage_id not given, return number of all stages of this type which have any actions stored.

        This function uses the fact that stage_id is guaranteed to be monotonic, if not consecutive.
        """

        previous_actions = self.get_actions(stage=stage_type)

        if stage_id:
            previous_actions = [a for a in previous_actions if a.stage_id < stage_id]

        previous_stage_ids = [a.stage_id for a in previous_actions]

        return len(set(previous_stage_ids))

    @db_scoped
    def send_secret_message(self, user_id: UUID, message: str):
        player = self.get_player(user_id)

        self.send_team_message(user_id, f"({player.user.name}) {message}")

    @db_scoped
    def send_team_message(self, user_id: UUID, message: str):
        role = self.get_player(user_id).role
        team = roles.get_role_team(role)
        role_description = roles.get_role_description(role)

        if not role_description.secret_chat_enabled:
            raise HTTPException(f"Role {role} does not have secret chat")
        if role_description.secret_chat_enabled is role_description.SecretChatType.TEAM:
            players_to_receive = [
                p.id for p in self.get_players() if roles.get_role_team(p.role) == team
            ]
        elif (
            role_description.secret_chat_enabled is role_description.SecretChatType.ROLE
        ):
            players_to_receive = [p.id for p in self.get_players() if p.role == role]

        self.send_chat_message(msg=f"{message}", player_list=players_to_receive)

    @db_scoped
    def get_hash_now(self):
        baked_query = bakery(lambda session: session.query(Game.update_tag))
        baked_query += lambda q: q.filter(Game.id == bindparam("game_id"))

        update_tag = baked_query(self._session).params(game_id=self.game_id).first()

        ret = update_tag[0] if update_tag else 0
        logger.info(f"Current hash {ret}, game {self.game_id}")
        return ret

    async def get_hash(self, known_hash=None, timeout=GET_HASH_TIMEOUT) -> int:
        """
        Gets the latest hash of this game

        If known_hash is provided and is the same as the current hash,
        do not return immediately: wait for up to timeout seconds.

        Note that this function is not @db_scoped, but it calls one that is:
        this is to prevent the database being locked while it waits
        """
        current_hash = self.get_hash_now()

        # Return immediately if the hash has changed or if there's no known hash
        if known_hash is None or known_hash != current_hash:
            return current_hash

        # Otherwise, lookup / make an event and subscribe to it
        if self.game_id not in update_events:
            update_events[self.game_id] = asyncio.Event()
            logger.info("Made new event for game %s", self.game_id)
        else:
            logger.info("Subscribing to event for %s", self.game_id)

        try:
            event = update_events[self.game_id]
            await asyncio.wait_for(event.wait(), timeout=timeout)
            logger.info(f"Event received for game {self.game_id}")
            return self.get_hash_now()
        except asyncio.TimeoutError:
            return current_hash

    @db_scoped
    def touch(self):
        self._session_modified = True
        self.get_game().touch()

    @db_scoped
    def player_keepalive(self, user_id: UUID):
        p = self.get_player(user_id, filter_by_activity=False)
        if not p:
            raise HTTPException(
                404, "You are not registered: refreshing now to join game"
            )

        logger.info("Keepalive player %s", user_id)

        # If the game has been modified, mark this
        self._check_for_dirty_session()

        # Touch the player then immediately flush, to prevent game state being marked as changed
        p.touch()
        self._session.flush()

        players = self.get_players(filter_by_activity=False)
        game = self.get_game()

        threshold = datetime.datetime.utcnow() - SPECTATOR_TIMEOUT

        # Mark any players who haven't been seen in a while as inactive. This
        # will only have an effect if the game is in particular states
        someone_changed = False

        for p in players:
            if p.active and p.last_seen <= threshold:
                logger.info(
                    f"Marking player {p.user.name} as inactive (p.last_seen="
                    f"{p.last_seen}, threshold={threshold})"
                )
                p.active = False
                someone_changed = True
            elif not p.active and p.last_seen > threshold:
                logger.info(f"Marking player {p.user.name} as active")
                p.active = True
                someone_changed = True

        if someone_changed:
            self.touch()
            # Reevaluate processed actions
            self.process_actions(game.stage, game.stage_id)

    @db_scoped
    def create_game(self):
        logger.info("Making new game %s", self.game_id)
        game = Game(id=self.game_id)

        self._session.add(game)

        return game

    @staticmethod
    def list_join(input_list):
        my_list = [str(i) for i in input_list]
        return " & ".join(
            [", ".join(my_list[:-1]), my_list[-1]] if len(my_list) > 2 else my_list
        )

    @db_scoped
    def end_game(self):
        game = self.get_game()

        # Give all the players another SPECTATOR_TIMEOUT before they are kicked for inactivity,
        # so people have time to see what happened
        for p in self.get_players():
            p.touch()

        # Delete all remaining actions
        del game.actions[:]

        # End the game
        self._set_stage(GameStage.ENDED)

    @db_scoped
    def move_to_lobby(self):
        # Delete all remaining actions
        game = self.get_game()
        del game.actions[:]

        self._wipe_all_roles()

        self._set_stage(GameStage.LOBBY)

    @db_scoped
    def _wipe_all_roles(self):
        # Wipe all existing roles
        for p in self.get_players(filter_by_activity=False):
            p.role = PlayerRole.SPECTATOR
            p.previous_role = PlayerRole.SPECTATOR
            p.state = PlayerState.SPECTATING

    @db_scoped
    def get_game_config_mode(self) -> Union[None, str]:
        g = self.get_game()

        if g is None:
            logger.debug("Game does not exist: using default")
            current_config = DistributionSettings()
        elif g.distribution_settings is None:
            logger.debug("No custom settings stored: using default mode")
            current_config = DistributionSettings()
        else:
            logger.debug(
                "Custom distribution settings [%s] found: comparing with modes",
                g.distribution_settings,
            )
            current_config = DistributionSettings.parse_obj(g.distribution_settings)

        for mode, config in LOOKUP_CONFIG.items():
            if config == current_config:
                logger.debug("Match found: mode is %s", mode)
                return mode

        # If there's no match, return "custom"
        return "custom"

    @db_scoped
    def set_game_config_mode(self, new_config_mode: str):
        logger.info("set_game_config_mode for game %s", self.game_id)

        g = self.get_game()

        if g is None:
            g = self.create_game()

        try:
            new_config = LOOKUP_CONFIG[new_config_mode]
        except KeyError:
            raise HTTPException(404, "{} is not a valid mode".format(new_config_mode))

        logger.info("Setting %s config to %s", self.game_id, new_config)
        g.distribution_settings = new_config.dict()

    @db_scoped
    def get_game_config(self) -> Union[None, DistributionSettings]:
        g = self.get_game()

        if g is None:
            logger.debug("Game does not exist: returning None")
            return None

        if g.distribution_settings is not None:
            logger.debug(
                "Custom distribution settings found: returning [%s]",
                g.distribution_settings,
            )
            return DistributionSettings.parse_obj(g.distribution_settings)
        else:
            logger.debug("No custom distribution settings: returning None")
            return None

    @db_scoped
    def set_game_config(self, new_config: Optional[DistributionSettings] = None):
        logger.info("set_game_config for game %s", self.game_id)

        g = self.get_game()

        if g is None:
            g = self.create_game()

        if new_config is None:
            logger.info("Setting %s config to defaults", self.game_id)
            g.distribution_settings = None
        else:
            if not isinstance(new_config, DistributionSettings):
                raise TypeError(
                    f"Expecting an instance of DistributionSettings, got {type(new_config)}"
                )

            if new_config.is_default():
                logger.info(
                    "New config is all defaults: setting %s to defaults",
                    self.game_id,
                )
                g.distribution_settings = None
            else:
                logger.info("Setting %s config to %s", self.game_id, new_config)
                g.distribution_settings = new_config.dict()

    @db_scoped
    def start_game(self):
        self._wipe_all_roles()

        # Assign new roles to the active players
        players = self.get_players()

        player_roles = roles.assign_roles(len(players), self.get_game_config())

        logger.info(
            "Assigning roles for {} game: {}".format(self.game_id, player_roles)
        )
        if not player_roles:
            raise HTTPException(status_code=400, detail="Not enough players")

        player: Player
        for player, role in zip(players, player_roles):
            player.role = role
            player.state = PlayerState.ALIVE
            player.seed = random.random()

        self.clear_chat_messages()
        self.clear_actions()
        self.send_chat_message("A new game has started. Night falls in the village")

        for player in players:
            apparant_role, desc = roles.get_apparant_role(player.role, GameStage.NIGHT)
            if desc.reveal_others_text:
                fellows = [p for p in players if p.role == player.role and p != player]
                if fellows:
                    self.send_chat_message(
                        f"You are a {apparant_role.value}! Your {desc.reveal_others_text} are "
                        f"{self.list_join(p.user.name for p in fellows)}",
                        player_list=[player.id],
                    )
                else:
                    self.send_chat_message(
                        f"You are a {apparant_role.value}! You're all by yourself...",
                        player_list=[player.id],
                    )
            else:
                self.send_chat_message(
                    f"You are a {apparant_role.value}!", player_list=[player.id]
                )

        for role in list(PlayerRole):
            roles.do_startup_callback(self, role)

        self._set_stage(GameStage.NIGHT)

    @db_scoped
    def get_messages(self, user_id: UUID, include_expired=False) -> List[ChatMessage]:
        """Get chat messages visible to the given user"""
        messages = self.get_game().messages
        player = self.get_player(user_id)

        visible_messages = [
            m for m in messages if not m.visible_to or player in m.visible_to
        ]

        if not include_expired:
            visible_messages = [m for m in visible_messages if not m.expired]

        # Format as ChatMessages
        return [
            ChatMessage(text=m.text, is_strong=m.is_strong) for m in visible_messages
        ]

    @db_scoped
    def clear_chat_messages(self):
        for m in self.get_game().messages:
            m.expired = True

    @db_scoped
    def clear_actions(self):
        for a in self.get_game().actions:
            a.expired = True

    @db_scoped
    def send_chat_message(self, msg, is_strong=False, user_list=[], player_list=[]):
        """Post a message in the chat log

        Args:
            msg (str): Message to post
            is_strong (bool, optional): Display with HTML <strong>? Defaults to
                                        False.
            user_list (List[UUID], optional): List of user IDs who can see the
                                        message. All players if None.
            player_list (List[int], optional): List of player IDs who can see the
                                        message. All players if None. Merged with user_list
        """
        m = Message(
            text=msg,
            is_strong=is_strong,
            game_id=self.game_id,
        )

        players = []

        for user_id in user_list:
            players.append(self.get_player(user_id))

        for player_id in player_list:
            players.append(self.get_player_by_id(player_id))

        for player in players:
            m.visible_to.append(player)

        g = self.get_game()
        g.messages.append(m)

    @db_scoped
    def kill_player(self, player_id, new_state: PlayerState):
        p = self.get_player_by_id(player_id)

        p.state = new_state

        # Change the player to a spectator, but remember what role they used to
        # have for displaying to the other players. If they get killed twice
        # (e.g. by the wolves and the vigilante) then don't do this twice. For
        # their state, they'll end up with the final kill: not ideal, but the
        # actual result is announced in the text still.
        if p.role != PlayerRole.SPECTATOR:
            p.previous_role = p.role
            p.role = PlayerRole.SPECTATOR

    @db_scoped
    def set_player_state(self, player_id, state: PlayerState):
        p = self.get_player_by_id(player_id)
        p.state = state

    @db_scoped
    def set_player_role(self, player_id, role: PlayerRole):
        p = self.get_player_by_id(player_id)
        p.role = role

    @db_scoped
    def vote_player(self, player_id):
        """Record a vote for a player

        Called by the execute() stage of vote actions
        """
        p = self.get_player_by_id(player_id)
        p.votes += 1

        logger.info(f"Player {p.user.name} has {p.votes} votes")

    @db_scoped
    def reset_votes(self):
        game = self.get_game()
        for p in self.get_players(filter_by_activity=False):
            p.votes = 0
        game.stage_id += 1
        logger.info("Votes reset")

    @db_scoped
    def process_actions(self, stage: GameStage, stage_id: int):
        """
        Process all the actions of the stage that just passed if all are in

        This function evaluates basically all the rules of the game. It is called
        by the role registered action functions when all the expected actions in
        a stage (usually the night) have been completed. It will parse the
        current state of the game and all the submitted actions, decide what
        should happen, dispatch the appropriate chat messages and alter the game
        state as required.
        """
        players = self.get_players()

        ready = True
        for player in players:
            role_action = roles.get_role_action(player.role, stage)

            if not role_action:
                continue

            round_end_behaviour = role_action.round_end_behaviour

            if (
                round_end_behaviour == resolver.RoundEndBehaviour.ONCE_OPTIONAL
                or round_end_behaviour == resolver.RoundEndBehaviour.MULTIPLE_OPTIONAL
            ):
                continue

            has_action, action_enabled = self.player_has_action(player, stage, stage_id)
            if has_action and action_enabled:
                logger.info("Stage not complete: %s has not acted", player.user.name)
                ready = False
                break

        if ready:
            logger.info(f"All the actions are in for game {self.game_id}: processing")
            resolver.process_actions(self, stage, stage_id)

    @db_scoped
    def _set_stage(self, stage: GameStage):
        """Change the stage of the game, updating the stage ID"""
        if not isinstance(stage, GameStage):
            raise ValueError

        g = self.get_game()
        g.stage = stage
        g.stage_id = Game.stage_id + 1
        g.num_attempts_this_stage = 0

    @db_scoped
    def get_user(self, user_id: UUID):
        u = self._session.query(User).get(user_id)
        return u

    @db_scoped
    def get_user_name(self, user_id: UUID):
        u = self.get_user(user_id)

        if not u:
            raise HTTPException(404, f"User {user_id} not found")

        return u.name

    @classmethod
    def set_user_name(cls, user_id: UUID, name: str):
        """
        Set a users's name

        Because this sets their name across all games, this method is a class method.

        Args:

        user_id (UUID): User ID
        name (str): New display name of the player
        """
        from . import database

        with database.session_scope() as s:
            u: User = s.query(User).get(user_id)

            if not u:
                u = cls.make_user(s, user_id)

            old_name = u.name

            if old_name == name:
                return

            if len(name) > MAX_NAME_LENGTH:
                name = name[:MAX_NAME_LENGTH]

            u.name = name
            u.name_is_generated = False

            # Bump all games in which this user plays
            for player_role in u.player_roles:
                WurwolvesGame.from_id(player_role.game_id, session=s).touch()

    @property
    @db_scoped
    def num_attempts_this_stage(self):
        return self.get_game().num_attempts_this_stage

    @num_attempts_this_stage.setter
    @db_scoped
    def num_attempts_this_stage(self, val):
        self.get_game().num_attempts_this_stage = val

    @db_scoped
    def is_role_present(
        self, role: Optional[PlayerRole], state: Optional[PlayerState] = None
    ) -> bool:
        """
        Is there at least one player with this role and stage in the game?
        """

        players = self.get_game().players

        if role:
            players = [p for p in players if p.role == role]

        if state:
            players = [p for p in players if p.state == state]

        return bool(players)

    @db_scoped
    def player_has_action(
        self, player: Union[int, Player], stage: GameStage, stage_id: int
    ):
        """Does this player have an action this turn? And have they already performed it?"""

        if isinstance(player, int):
            player_lookup = self.get_player_by_id(player)
            if player_lookup is None:
                raise ValueError("Player id {} not found in database".format(player))
            player = player_lookup

        action_class = roles.get_role_action(player.role, stage)

        # If there's no action_class, there's no action
        if not action_class:
            return False, False

        logger.debug(
            f"player.state = {player.state}, action_class.allowed_player_states = {action_class.allowed_player_states}"
        )

        # Player has an action in this stage...
        has_action = (
            player.state in action_class.allowed_player_states
            and action_class.is_action_available(self, stage, stage_id, player.id)
        )

        if not has_action:
            action_enabled = False
        # ...that doesn't require them to be active or it does, and they are
        elif action_class.active_players_only and not player.active:
            action_enabled = False
        #  ..and they hasn't yet acted
        elif (
            action_class.round_end_behaviour
            == resolver.RoundEndBehaviour.MULTIPLE_OPTIONAL
        ):
            action_enabled = True
        elif action_class.team_action == resolver.TeamBehaviour.ONCE_PER_TEAM:
            # Which roles are on my team?
            my_team = roles.get_role_team(player.role)
            my_team_roles = [
                role
                for role in list(PlayerRole)
                if roles.get_role_team(role) == my_team
            ]

            actions = [a for a in self.get_game().actions if a.stage_id == stage_id]
            actions_by_my_team = [a for a in actions if a.role in my_team_roles]

            action_enabled = not bool(actions_by_my_team)
        else:
            action_enabled = not any(a.stage_id == stage_id for a in player.actions)

        return has_action, action_enabled

    @staticmethod
    def generate_name():
        global names
        if not names:
            with open(NAMES_FILE, newline="") as f:
                names = list(line.rstrip() for line in f.readlines())

        name = " ".join([random.choice(names), random.choice(names)]).title()

        return name

    @db_scoped
    def parse_game_to_state(self, user_id: UUID) -> FrontendState:
        """
        Parse this game into a FrontendState for viewing by the user user_id
        """

        if logger.isEnabledFor(logging.DEBUG):
            t_start = time.time()
            logger.debug(f"Starting parse_game_to_state")

        game = self.get_game()

        logger.debug("Game is loaded from database")

        if not game:
            self.join(user_id)
            game = self.get_game()

        players = self.get_players()

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logger.debug("Players: %s", [p.user.name for p in players])

        try:
            player = [p for p in players if p.user_id == user_id][0]
        except IndexError:
            self.join(user_id)

            game = self.get_game()
            players = game.players
            player = [p for p in players if p.user_id == user_id][0]

        logger.debug("Game: %s", game)
        logger.debug("Player: %s", player)
        logger.debug("User id: %s", user_id)
        logger.debug("Game players: %s", players)

        # Get the role description
        apparant_role, role_details = get_apparant_role(player.role, game.stage)

        action_desc = role_details.get_stage_action(game.stage)

        has_action, action_enabled = self.player_has_action(
            player, game.stage, game.stage_id
        )

        logger.debug(
            f"Player {player.user.name} is a {player.role.value}, has_action={has_action}, action_enabled={action_enabled}"
        )

        controls_state = FrontendState.RoleState(
            title=role_details.display_name,
            text=action_desc.text[player.state],
            role=apparant_role,
            seed=player.seed,
            button_visible=has_action,
            button_enabled=action_enabled,
            button_text=action_desc.button_text,
            button_submit_person=action_desc.button_text and action_desc.select_person,
            button_submit_func=get_action_func_name(player.role, game.stage),
        )

        logger.debug("role_details.stages: {}".format(role_details.stages))
        logger.debug("action_desc: {}".format(action_desc))
        logger.debug("controls_state: {}".format(controls_state))

        player_states = []
        for p in players:

            status = p.state

            ready = False
            if game.stage in [
                GameStage.LOBBY,
                GameStage.ENDED,
                GameStage.VOTING,
                GameStage.DAY,
            ]:
                has_action, action_enabled = self.player_has_action(
                    p, game.stage, game.stage_id
                )
                if has_action and not action_enabled:
                    ready = True

            # Display real role if the game is ended or this player should be able to see it
            real_role = p.role
            if (
                p.previous_role
                and (p.role == PlayerRole.SPECTATOR or p.role == PlayerRole.NARRATOR)
                and p.state != PlayerState.SPECTATING
            ):
                real_role = p.previous_role
            displayed_role = PlayerRole.VILLAGER

            # Only display as a spectator if the player is a spectator/narrator and had no
            # previous role
            if real_role == PlayerRole.SPECTATOR or real_role == PlayerRole.NARRATOR:
                displayed_role = PlayerRole.SPECTATOR
            elif p.id == player.id:
                if player.state.is_dead():
                    displayed_role = real_role
                else:
                    displayed_role = apparant_role
            elif (
                player.role == PlayerRole.NARRATOR
                or (real_role == PlayerRole.WOLF and player.role == PlayerRole.WOLF)
                or (real_role == PlayerRole.ACOLYTE and player.role == PlayerRole.WOLF)
                or (real_role == PlayerRole.JESTER and player.role == PlayerRole.WOLF)
                or (real_role == PlayerRole.MASON and player.role == PlayerRole.MASON)
                or (real_role == PlayerRole.JESTER and p.state == PlayerState.LYNCHED)
                or game.stage == GameStage.ENDED
                or (
                    real_role == PlayerRole.MAYOR
                    and self.num_previous_stages(GameStage.NIGHT, game.stage_id) > 0
                )
            ):
                displayed_role = real_role

            player_states.append(
                FrontendState.UIPlayerState(
                    id=p.user_id,
                    name=p.user.name,
                    status=status,
                    role=displayed_role,
                    seed=p.seed,
                    selected=False,
                    ready=ready,
                )
            )

        # Random sort
        player_states.sort(key=lambda s: s.seed)

        state = FrontendState(
            state_hash=game.update_tag,
            players=player_states,
            chat=[
                FrontendState.ChatMsg(msg=m.text, isStrong=m.is_strong)
                for m in game.messages
                if not m.expired
                and ((not m.visible_to) or any(player.id == v.id for v in m.visible_to))
            ],
            showSecretChat=bool(role_details.secret_chat_enabled),
            stage=game.stage,
            controls_state=controls_state,
            myID=user_id,
            myName=player.user.name,
            myNameIsGenerated=player.user.name_is_generated,
            myStatus=player.state,
            isCustomized=game.distribution_settings is not None,
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Full UI state: %s", state)

            t_end = time.time()
            logger.debug(
                f"Ending parse_game_to_state, duration = {t_end - t_start :.3f}s"
            )

        return state


def trigger_update_event(game_id: int):
    logger.info(f"Triggering updates for game {game_id}")
    global update_events
    if game_id in update_events:
        update_events[game_id].set()
        del update_events[game_id]


def _filter_by_activity(q):
    """
    Show all players who are active, and all players who have/had a non-spectator role,
    """
    return q.filter(
        or_(
            Player.active,
            Player.role != PlayerRole.SPECTATOR,
            Player.previous_role != PlayerRole.SPECTATOR,
        )
    )


def _player_is_active(p: Player):
    """
    Given a player, decide if they are active in the game
    """
    return (
        p.active
        or p.role != PlayerRole.SPECTATOR
        or (p.previous_role and p.previous_role != PlayerRole.SPECTATOR)
    )


# Not currently used:
#
# class SwitchStage(resolver.GameAction):
#     """
#     This action does nothing! It just records that the stage has been switched.
#     Unlike most role actions, this one has no originator and no target. It simple exists in the
#     action log and does nothing when called, to serve as a log that the stage occured.

#     Later, I could expand the game to expect this action to exist before process_actions succeeds.
#     Then, I could submit this action on a timer to end the rounds automatically. Now, however, this
#     does not happen: process_actions does not expect this action to be present, but won't complain if
#     it is.

#     Currently, this action is submitted by _set_stage() to serve as a marker.
#     """


# Create API endpoints and methods in WurwolvesGame for all the role actions
roles.register_roles(WurwolvesGame)
