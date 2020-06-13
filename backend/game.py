'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
import os
import random
from functools import wraps
from typing import List
from uuid import UUID

import pydantic

from .model import (Game, GameStage, Message, Player, PlayerRole, PlayerState,
                    User, hash_game_id)

NAMES_FILE = os.path.join(os.path.dirname(__file__), 'names.txt')
names = None


class ChatMessage(pydantic.BaseModel):
    text: str
    is_strong = False


class WurwolvesGame:
    """
    Provides methods for accessing all the properties of a wurwolves game. This
    object is initialised with the ID of a game and loads all other information
    from the database on request.
    """

    def __init__(self, game_id: str):
        '''Make a new WurwolvesGame for controlling / getting information about a game

        Arguments:
        game_id (str): ID of the game. This will be hashed to become the database id
        '''
        self.game_id = hash_game_id(game_id)
        self.session = None
        self.session_users = 0

    def db_scoped(func):
        """
        Start a session and store it in self.session

        When a @db_scoped method returns, commit the session

        Close the session once all @db_scoped methods are finished
        """
        from . import database

        @wraps(func)
        def f(self, *args, **kwargs):
            if not self.session:
                self.session = database.Session()

            try:
                self.session_users += 1
                out = func(self, *args, **kwargs)
                self.session.commit()
                return out
            except Exception as e:
                self.session.rollback()
                raise e
            finally:
                self.session_users -= 1
                if self.session_users == 0:
                    self.session.close()
                    self.session = None
        return f

    @db_scoped
    def set_player(self, user_id: UUID, name: str):
        """
        Update a player's name

        Args:

        user_id (UUID): User ID
        name (str): New display name of the player
        """
        u = self.session.query(User).filter(User.id == user_id).first()
        u.name = name
        u.name_is_generated = False
        self.session.add(u)

    @db_scoped
    def join(self, user_id: UUID):
        """Join or rejoin a game as a user

        Args:
            user_ID (str): ID of the user
        """

        print(f"User {user_id} joining now")

        # Get the user from the user list, adding them if not already present
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            user = User(
                id=user_id,
                name=WurwolvesGame.generate_name(),
                name_is_generated=True,
            )

            print("Making new player {} = {}".format(user.id, user.name))

        # Get the game, creating it if it doesn't exist
        game = self.get_game()
        if not game:
            game = self.create_game()

        # Add this user to the game as a spectator if they're not already in it
        player = self.session.query(Player).filter(Player.game == game, Player.user == user).first()

        if not player:
            player = Player(
                game=game,
                user=user,
                role=PlayerRole.SPECTATOR,
                state=PlayerState.ALIVE,
            )

        self.session.add(game)
        self.session.add(user)
        self.session.add(player)

    @db_scoped
    def get_game(self) -> Game:
        return self.session.query(Game).filter(Game.id == self.game_id).first()

    @db_scoped
    def get_player(self, user_id: UUID) -> Player:
        return self.session.query(Player).filter(
            Player.game_id == self.game_id,
            Player.user_id == user_id
        ).first()

    @db_scoped
    def create_game(self):
        game = Game(id=self.game_id)

        self.session.add(game)

        return game

    @db_scoped
    def start_game(self):
        game = self.get_game()

        game.stage = GameStage.NIGHT

        player: Player
        for player in game.players:
            # For now, just assign some random roles
            player.role = random.choice(list(PlayerRole))

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

        self.session.add(m)

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
