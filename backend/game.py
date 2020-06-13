'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
import os
import random
from enum import Enum
from functools import wraps
from uuid import UUID

from .model import (Game, Message, Player, PlayerRole, PlayerState, User,
                    hash_game_id)

NAMES_FILE = os.path.join(os.path.dirname(__file__), 'names.txt')
names = None


class GameStages(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"
    VOTING = "VOTING"


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

    def scoped(func):
        """
        Start a session and store it in self.session

        When a @scoped method returns, commit the session

        Close the session once all users are finished
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
            except Exception:
                self.session.rollback()
                raise
            finally:
                self.session_users -= 1
                if self.session_users == 0:
                    self.session.close()
                    self.session = None
        return f

    @scoped
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

    # def get_player_status(self, user_id):
    #     """Get the status of the requested player

    #     Returns:
    #         Tuple[str, str]: Name and current status of player
    #     """
    #     q = EventQueue(
    #         self.game_id,
    #         type_filter=EventType.UPDATE_PLAYER,
    #     )
    #     player_name = None
    #     status = None

    #     for rename_event in q.get_all_events():
    #         if rename_event.details['id'] == user_id:
    #             player_name = rename_event.details['name']
    #             status = rename_event.details['status']

    #     return player_name, status

    @scoped
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
        game = self.session.query(Game).filter(Game.id == self.game_id).first()

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

    @scoped
    def create_game(self):
        game = Game(id=self.game_id)
        self.add_dummy_messages()

        self.session.add(game)

        return game

#     def new_player(self, name: str = None):

#         self.set_player(name, "spectating")

#     def start_game(self):
#         role_details = {
#             "title": "Started!",
#             "day_text": '''
# The game has started!

# I should probably write some more things here.
#             '''.strip(),
#             "night_text": "",
#             "button_visible": False,
#         }

#         players = self.get_current_players()
#         print(players)

#         role_events = []
#         for p in players:
#             self.set_player(None, Stati.NORMAL, user_id=p)

#         ui_event = UIEvent(type=UIEventType.SET_CONTROLS, payload=role_details)

#         with session_scope() as session:
#             session.add(GameEvent(
#                 game_id=self.game_id,
#                 event_type=EventType.GUI,
#                 public_visibility=True,
#                 details=ui_event.dict(),
#             ))
#             for e in role_events:
#                 session.add(e)

#         players = self.get_current_players()
#         print(players)

#     def get_current_players(self):
#         """Get a list of current players in the game, with their states and roles
#         """
#         q = EventQueue(self.game_id, type_filter=[EventType.UPDATE_PLAYER,
#                                                   EventType.REMOVE_PLAYER,
#                                                   EventType.SET_ROLE])

#         players = {}
#         for event in q.get_all_events():
#             if event.event_type == EventType.UPDATE_PLAYER:
#                 d = UpdatePlayerEvent.parse_obj(event.details)
#                 if d.id not in players:
#                     players[d.id] = {
#                         'name': d.name,
#                         'status': d.status,
#                         'role': None,
#                     }
#                 else:
#                     if d.name:
#                         players[d.id]["name"] = d.name
#                     if d.status:
#                         players[d.id]["status"] = d.status
#             elif event.event_type == EventType.SET_ROLE:
#                 d = SetRoleEvent.parse_obj(event.details)
#                 players[d.id]["role"] = d.role
#             elif event.event_type == EventType.REMOVE_PLAYER:
#                 d = RemovePlayerEvent.parse_obj(event.details)
#                 del players[d.id]

#         return players

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

    def send_chat_message(self, msg, is_strong=False, player_list=[]):
        """Post a message in the chat log

        Args:
            msg (str): Message to post
            is_strong (bool, optional): Display with HTML <strong>? Defaults to
                                        False.
            player_list (List[Integer], optional): List of player IDs who can see the
                                        message. All players if None. 
        """
        m = Message(
            text=msg,
            is_strong=is_strong,
        )

        for player_id in player_list:
            m.visible_to.add(player_id)

        self.session.add(m)

    # def set_stage(self, new_stage: GameStages):
    #     with session_scope() as session:
    #         session.add(GameEvent(
    #             game_id=self.game_id,
    #             event_type=EventType.GUI,
    #             public_visibility=True,
    #             details=UIEvent(type=UIEventType.GAME_STAGE, payload={"stage": new_stage}).dict(),
    #         ))

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
