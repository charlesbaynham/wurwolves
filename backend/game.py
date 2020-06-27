"""
Game module

This module provides the WurwolvesGame class, for interacting with a single game
"""
import asyncio
import datetime
import logging
import os
import random
from functools import wraps
from typing import Dict, List, Optional, Union
from uuid import UUID

import pydantic
from fastapi import HTTPException

from . import resolver, roles
from .model import (
    Action,
    ActionModel,
    Game,
    GameModel,
    GameStage,
    Message,
    Player,
    PlayerModel,
    PlayerRole,
    PlayerState,
    User,
    hash_game_tag,
)

SPECTATOR_TIMEOUT = datetime.timedelta(seconds=40)

NAMES_FILE = os.path.join(os.path.dirname(__file__), "names.txt")
names = None

update_events: Dict[int, asyncio.Event] = {}


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

    def db_scoped(func):
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
                if not self._session_modified and (
                    self._session.dirty or self._session.new
                ):
                    self._session_modified = True
                self._session.commit()
                return out
            except Exception as e:
                self._session.rollback()
                raise e
            finally:
                # If we're about to close the session, check if the game should be marked as updated
                if self._session_users == 1 and self._session_modified:
                    # If any of the functions altered the game state,
                    # fire the corresponding updates events if they are present in the global dict
                    # And mark the game as altered in the database
                    g = self.get_game()
                    g.touch()
                    self._session.add(g)
                    self._session.commit()
                    trigger_update_event(self.game_id)

                self._session_users -= 1

                # Close the session if we made it and no longer need it
                if self._session_users == 0 and not self._session_is_external:
                    self._session.close()
                    self._session = None

        return f

    @db_scoped
    def set_player(self, user_id: UUID, name: str):
        """
        Update a player's name

        Args:

        user_id (UUID): User ID
        name (str): New display name of the player
        """
        u = self._session.query(User).filter(User.id == user_id).first()
        u.name = name
        u.name_is_generated = False
        self._session.add(u)

    @db_scoped
    def join(self, user_id: UUID):
        """Join or rejoin a game as a user

        Args:
            user_ID (str): ID of the user
        """

        logging.info("User %s joining now", user_id)

        # Get the user from the user list, adding them if not already present
        user = self._session.query(User).filter(User.id == user_id).first()

        if not user:
            user = User(
                id=user_id, name=WurwolvesGame.generate_name(), name_is_generated=True,
            )

            print("Making new player {} = {}".format(user.id, user.name))

        # Get the game, creating it if it doesn't exist
        game = self.get_game()
        if not game:
            game = self.create_game()

        # Add this user to the game as a spectator if they're not already in it
        player = (
            self._session.query(Player)
            .filter(Player.game == game, Player.user == user)
            .first()
        )

        if not player:
            player = Player(
                game=game,
                user=user,
                role=PlayerRole.SPECTATOR,
                state=PlayerState.SPECTATING,
            )
            self.send_chat_message(f"{player.user.name} joined the game", True)

        self._session.add(game)
        self._session.add(user)
        self._session.add(player)

    @db_scoped
    def get_game(self) -> Game:
        return self._session.query(Game).filter(Game.id == self.game_id).first()

    @db_scoped
    def get_game_model(self) -> GameModel:
        g = self.get_game()
        return GameModel.from_orm(g) if g else None

    @db_scoped
    def get_player_id(self, user_id: UUID) -> int:
        return (
            self._session.query(Player.id)
            .filter(Player.game_id == self.game_id, Player.user_id == user_id)
            .first()
        )[0]

    @db_scoped
    def get_player(self, user_id: UUID) -> Player:
        return (
            self._session.query(Player)
            .filter(Player.game_id == self.game_id, Player.user_id == user_id)
            .first()
        )

    @db_scoped
    def get_player_by_id(self, player_id: int) -> Player:
        return self._session.query(Player).filter(Player.id == player_id).first()

    @db_scoped
    def get_player_model(self, user_id: UUID) -> PlayerModel:
        p = self.get_player(user_id)
        return PlayerModel.from_orm(p) if p else None

    @db_scoped
    def get_player_model_by_id(self, player_id: int) -> PlayerModel:
        p = self.get_player_by_id(player_id)
        return PlayerModel.from_orm(p) if p else None

    @db_scoped
    def get_players(self) -> List[Player]:
        return self._session.query(Player).filter(Player.game_id == self.game_id).all()

    @db_scoped
    def get_players_model(self) -> List[PlayerModel]:
        return [PlayerModel.from_orm(p) for p in self.get_players()]

    @db_scoped
    def get_actions(self, stage_id=None, player_id: int = None) -> List[Action]:
        """ Get orm objects for any actions performed by the given user in the given stage. Default to the current stage. 
        """
        game = self.get_game()

        if stage_id is None:
            stage_id = game.stage_id

        q = self._session.query(Action).filter(
            Action.game_id == game.id, Action.stage_id == game.stage_id
        )

        if player_id:
            q = q.filter(Action.player_id == player_id)

        return q.all()

    @db_scoped
    def get_actions_model(
        self, stage_id=None, player_id: int = None
    ) -> List[ActionModel]:
        """ Get models for any actions performed by the given user in the given stage. Default to the current stage. 
        """
        return [ActionModel.from_orm(a) for a in self.get_actions(stage_id, player_id)]

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
        players_on_team = [
            p.id for p in self.get_players() if roles.get_role_team(p.role) == team
        ]
        self.send_chat_message(msg=f"{message}", player_list=players_on_team)

    @db_scoped
    def get_hash_now(self):
        g = self.get_game()
        return g.update_counter if g else 0

    async def get_hash(self, known_hash=None, timeout=15) -> int:
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
            logging.info("Made new event for %s", self.game_id)
        else:
            logging.info("Subscribing to event for %s", self.game_id)

        try:
            event = update_events[self.game_id]
            await asyncio.wait_for(event.wait(), timeout=timeout)
            logging.info(f"Event received for game {self.game_id}")
            return self.get_hash_now()
        except asyncio.TimeoutError:
            return current_hash

    @db_scoped
    def player_keepalive(self, user_id: UUID):
        u = self.get_user(user_id)
        u.touch()
        self._session.commit()

        players = self.get_players()
        game = self.get_game()

        threshold = datetime.datetime.utcnow() - SPECTATOR_TIMEOUT

        # Clear out any old players
        for p in players:
            if (
                p.role == PlayerRole.SPECTATOR or game.stage == GameStage.ENDED
            ) and p.user.last_seen < threshold:
                logging.info(
                    f"Remove player {p.user.name} for inactivity (p.user.last_seen="
                    f"{p.user.last_seen}, threshold={threshold}"
                )
                self.send_chat_message(f"{p.user.name} has left the game")
                self._session.delete(p)
                self.get_game().touch()

                # Reevaluate processed actions
                self.process_actions(game.stage, game.stage_id)

    @db_scoped
    def create_game(self):
        game = Game(id=self.game_id)

        self._session.add(game)

        return game

    @staticmethod
    def list_join(input_list):
        my_list = [str(i) for i in input_list]
        return "&".join(
            [",".join(my_list[:-1]), my_list[-1]] if len(my_list) > 2 else my_list
        )

    @db_scoped
    def start_game(self):
        game = self.get_game()

        player_roles = roles.assign_roles(len(game.players))

        logging.info(
            "Assigning roles for {} game: {}".format(self.game_id, player_roles)
        )
        if not player_roles:
            raise HTTPException(status_code=400, detail="Not enough players")

        player: Player
        for player, role in zip(game.players, player_roles):
            player.role = role
            player.state = PlayerState.ALIVE

        self.clear_chat_messages()
        self.send_chat_message("A new game has started. Night falls in the village")

        for player in game.players:
            desc = roles.get_role_description(player.role)
            if desc.reveal_others_text:
                fellows = [
                    p for p in game.players if p.role == player.role and p != player
                ]
                if fellows:
                    self.send_chat_message(
                        f"You are a {player.role.value}! Your {desc.reveal_others_text} are "
                        f"{self.list_join(p.user.name for p in fellows)}",
                        player_list=[player.id],
                    )
                else:
                    self.send_chat_message(
                        f"You are a {player.role.value}! You're all by yourself...",
                        player_list=[player.id],
                    )
            else:
                self.send_chat_message(
                    f"You are a {player.role.value}!", player_list=[player.id]
                )

        self._set_stage(GameStage.NIGHT)

    @db_scoped
    def get_messages(self, user_id: UUID) -> List[ChatMessage]:
        """ Get chat messages visible to the given user """

        game = self.get_game()

        out = []

        player = self.get_player(user_id)

        m: Message
        for m in game.messages:
            if m.visible_to and player not in m.visible_to:
                continue

            out.append(ChatMessage(text=m.text, is_strong=m.is_strong))

        return out

    @db_scoped
    def clear_chat_messages(self):
        for m in self.get_game().messages:
            self._session.delete(m)

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
        m = Message(text=msg, is_strong=is_strong, game_id=self.game_id,)

        players = []

        for user_id in user_list:
            players.append(self.get_player(user_id))

        for player_id in player_list:
            players.append(self.get_player_by_id(player_id))

        for player in players:
            m.visible_to.append(player)

        self._session.add(m)

    @db_scoped
    def vote_start(self):
        g = self.get_game()
        g.start_votes = Game.start_votes + 1
        self._session.commit()

        logging.info(f"({self.game_id}) g.start_votes = {g.start_votes}")

        if g.start_votes == len(g.players):
            logging.warning("({}) all votes are in: starting".format(self.game_id))
            self.start_game()
            g.start_votes = 0

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
        """ Record a vote for a player

        Called by the execute() stage of vote actions
        """
        p = self.get_player_by_id(player_id)
        p.votes = Player.votes + 1
        self._session.commit()

        logging.info(f"Player {p.user.name} has {p.votes} votes")

    @db_scoped
    def reset_votes(self):
        game = self.get_game()
        for p in game.players:
            p.votes = 0
        game.stage_id += 1
        logging.info("Votes reset")

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
            has_action, action_enabled = self.player_has_action(player, stage, stage_id)
            if has_action and action_enabled:
                ready = False
                break

        if ready:
            logging.info(f"All the actions are in for game {self.game_id}: processing")
            resolver.process_actions(self, stage, stage_id)

    @db_scoped
    def _set_stage(self, stage: GameStage):
        """ Change the stage of the game, updating the stage ID """
        if not isinstance(stage, GameStage):
            raise ValueError

        g = self.get_game()
        g.stage = stage
        g.stage_id = Game.stage_id + 1

    @db_scoped
    def get_user(self, user_id: UUID):
        u = self._session.query(User).filter_by(id=user_id).first()
        if not u:
            raise KeyError(f"User {user_id} does not exist")
        return u

    @db_scoped
    def get_user_name(self, user_id: UUID):
        u = self.get_user(user_id)
        return u.name

    @classmethod
    def set_user_name(cls, user_id: UUID, name: str):
        """
        Set a users's name

        Because this sets their name across all games, this method is a class method. 
        """
        from . import database

        with database.session_scope() as s:
            u: User = s.query(User).filter(User.id == user_id).first()

            old_name = u.name

            if old_name == name:
                return

            u.name = name
            u.name_is_generated = False

            # Send a message to all games in which this user plays
            for player_role in u.player_roles:
                WurwolvesGame.from_id(player_role.game_id, session=s).send_chat_message(
                    msg=f"{old_name} has changed their name to {name}"
                )

    @db_scoped
    def is_role_present(
        self, role: Optional[PlayerRole], state: Optional[PlayerState] = None
    ) -> bool:
        """
        Is there at least one player with this role and stage in the game?
        """

        q = self._session.query(Player).filter(Player.game_id == self.game_id)

        if role:
            q = q.filter(Player.role == role)

        if state:
            q = q.filter(Player.state == state)

        return bool(q.first())

    @db_scoped
    def player_has_action(
        self, player: Union[int, Player], stage: GameStage, stage_id: int
    ):
        """Does this player have an action this turn? And have they already performed it?"""

        if isinstance(player, int):
            player = self.get_player_by_id(player)

        action_class = roles.get_role_action(player.role, stage)

        # If there's no action_class, there's no action
        if not action_class:
            return False, False

        # Player has an action in this stage...
        has_action = (
            player.state in action_class.allowed_player_states
            and action_class.is_action_available(self, stage, stage_id, player.id)
        )

        #  ..and hasn't yet acted
        if not has_action:
            action_enabled = False
        elif action_class.team_action:
            # Which roles are on my team?
            my_team = roles.get_role_team(player.role)
            my_team_roles = [
                role
                for role in list(PlayerRole)
                if roles.get_role_team(role) == my_team
            ]

            team_actions = (
                self._session.query(Action)
                .join(Action.player)
                .filter(
                    Action.game_id == self.game_id,
                    Action.stage_id == stage_id,
                    Player.role.in_(my_team_roles),
                )
                .all()
            )

            action_enabled = not bool(team_actions)
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


def trigger_update_event(game_id: int):
    logging.info(f"Triggering updates for game {game_id}")
    global update_events
    if game_id in update_events:
        update_events[game_id].set()
        del update_events[game_id]


# Create API endpoints and methods in WurwolvesGame for all the role actions
roles.register_roles(WurwolvesGame)
