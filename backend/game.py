'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
import asyncio
import logging
import os
import random
from functools import wraps
from typing import Dict, List
from uuid import UUID

import pydantic

from . import roles
from .model import (Game, GameModel, GameStage, Message, Player, PlayerModel,
                    PlayerRole, PlayerState, User, hash_game_tag)

NAMES_FILE = os.path.join(os.path.dirname(__file__), 'names.txt')
names = None

update_events: Dict[int, asyncio.Event] = {}


class ChatMessage(pydantic.BaseModel):
    text: str
    is_strong = False


class WurwolvesGame(roles.MedicMixin):
    """
    Provides methods for accessing all the properties of a wurwolves game. This
    object is initialised with the ID of a game and loads all other information
    from the database on request.
    """

    def __init__(self, game_tag: str, session=None):
        '''Make a new WurwolvesGame for controlling / getting information about a game

        Arguments:
        game_tag (str): Tag of the game. This will be hashed to become the database id
        '''
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
                if not self._session_modified and (self._session.dirty or self._session.new):
                    self._session_modified = True
                self._session.commit()
                return out
            except Exception as e:
                self._session.rollback()
                raise e
            finally:
                self._session_users -= 1
                if self._session_users == 0:
                    # If any of the functions altered the game state,
                    # fire the corresponding updates events if they are present in the global dict
                    if self._session_modified:
                        trigger_update_event(self.game_id)

                    # Close the session if we made it and no longer need it
                    if not self._session_is_external:
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

        print(f"User {user_id} joining now")

        altered_game = False

        # Get the user from the user list, adding them if not already present
        user = self._session.query(User).filter(User.id == user_id).first()

        if not user:
            user = User(
                id=user_id,
                name=WurwolvesGame.generate_name(),
                name_is_generated=True,
            )
            altered_game = True

            print("Making new player {} = {}".format(user.id, user.name))

        # Get the game, creating it if it doesn't exist
        game = self.get_game()
        if not game:
            game = self.create_game()

        # Add this user to the game as a spectator if they're not already in it
        player = self._session.query(Player).filter(Player.game == game, Player.user == user).first()

        if not player:
            player = Player(
                game=game,
                user=user,
                role=PlayerRole.SPECTATOR,
                state=PlayerState.SPECTATING,
            )
            altered_game = True
            self.send_chat_message(
                f"{player.user.name} joined the game",
                True
            )

        self._session.add(game)
        self._session.add(user)
        self._session.add(player)

        if altered_game:
            game.touch()

    @db_scoped
    def get_game(self) -> Game:
        return self._session.query(Game).filter(Game.id == self.game_id).first()

    @db_scoped
    def get_game_model(self) -> GameModel:
        g = self.get_game()
        return GameModel.from_orm(g) if g else None

    @db_scoped
    def get_player(self, user_id: UUID) -> Player:
        return self._session.query(Player).filter(
            Player.game_id == self.game_id,
            Player.user_id == user_id
        ).first()

    @db_scoped
    def get_player_model(self, user_id: UUID) -> PlayerModel:
        p = self.get_player(user_id)
        return PlayerModel.from_orm(p) if p else None

    @db_scoped
    def get_players(self, user_id: UUID) -> List[Player]:
        return self._session.query(Player).filter(
            Player.game_id == self.game_id
        ).all()

    @db_scoped
    def get_players_model(self, user_id: UUID) -> List[PlayerModel]:
        return [
            PlayerModel.from_orm(p) for p in self.get_players()
        ]

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
    def create_game(self):
        game = Game(id=self.game_id)

        self._session.add(game)

        return game

    @db_scoped
    def start_game(self):
        game = self.get_game()

        self._session.add(game)

        game.stage = GameStage.NIGHT

        player: Player
        for player in game.players:
            # For now, just assign some random roles
            non_spectator_roles = list(PlayerRole)
            non_spectator_roles.remove(PlayerRole.SPECTATOR)
            player.role = random.choice(non_spectator_roles)
            player.state = PlayerState.ALIVE

        self.add_dummy_messages()

    def add_dummy_messages(self):
        messages = [
            ("3 votes for Euan (Rosie, Rachel, Gaby)", False),
            ("Gaby was voted off", True),
            ("Sophie was killed in the night", True),
            ("Rob was nominated by Charles", False),
            ("James was nominated by Charles", False),
            ("James was seconded by Parav", False),
            ("4 votes for Gaby (Charles, James, Parav, Harry)", False),
            ("3 votes for Euan (Rosie, Rachel, Gaby)", False),
            ("Gaby was voted off", True),
            ("Sophie was killed in the night", True),
            ("Rob was nominated by Charles", False),
            ("James was nominated by Charles", False),
            ("James was seconded by Parav", False),
            ("4 votes for Gaby (Charles, James, Parav, Harry)", False),
            ("3 votes for Euan (Rosie, Rachel, Gaby)", False),
            ("Gaby was voted off", True),
            ("Sophie was killed in the night", True),
            ("Rob was nominated by Charles", False),
            ("James was nominated by Charles", False)
        ]

        for msg, is_strong in messages:
            self.send_chat_message(msg, is_strong)

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
    def send_chat_message(self, msg, is_strong=False, user_list=[]):
        """Post a message in the chat log

        Args:
            msg (str): Message to post
            is_strong (bool, optional): Display with HTML <strong>? Defaults to
                                        False.
            user_list (List[UUID], optional): List of user IDs who can see the
                                        message. All players if None. 
        """
        m = Message(
            text=msg,
            is_strong=is_strong,
            game_id=self.game_id,
        )

        for user_id in user_list:
            m.visible_to.append(
                self.get_player(user_id)
            )

        self._session.add(m)

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
            # Manually trigger update and touch game. This shouldn't be required
            # but is for some reason...
            for player_role in u.player_roles:
                WurwolvesGame.from_id(player_role.game_id, session=s).send_chat_message(
                    msg=f"{old_name} has changed their name to {name}"
                )
                player_role.game.touch()
                trigger_update_event(player_role.game_id)

    @staticmethod
    def generate_name():
        global names
        if not names:
            with open(NAMES_FILE, newline='') as f:
                names = list(line.rstrip() for line in f.readlines())

        name = " ".join([
            random.choice(names),
            random.choice(names)
        ]).title()

        return name


def trigger_update_event(game_id: int):
    logging.info(f"Triggering updates for game {game_id}")
    global update_events
    if game_id in update_events:
        update_events[game_id].set()
        del update_events[game_id]


# Register the roles
roles.register(WurwolvesGame, "medic", PlayerRole.MEDIC)
