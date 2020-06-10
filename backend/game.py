'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
import os
import random
from enum import Enum
from uuid import UUID

from .database import session_scope
from .events import (EventQueue, RemovePlayerEvent, Stati, UIEvent,
                     UIEventType, UpdatePlayerEvent, SetRoleEvent)
from .model import EventType, GameEvent, GameEventVisibility, hash_game_id

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

    The data describing a game is stored as a series of events in an event log.
    To recover the state of a game, the server therefore replays all events in
    the log from start to end. See the :class:`backend.model.GameEvent` for the
    database model and :mod:`backend.events` for methods that access the queue
    and filter it.

    If user_ID is provide, associate this instance with a particular user for
    some functions. 

    Note that :mod:`backend.events` does not provide methods for altering the
    queue. This is intentional: all write access is performed through this
    module instead.     
    """

    def __init__(self, game_id: str, user_id: UUID = None):
        self.game_id = hash_game_id(game_id)
        self.user_id = user_id
        self.latest_event_id = None

    def set_player(self, name: str, status: str, user_id: UUID = None):
        """
        Update a player's name and status

        Updates a player's state in the game. If not already present, adds
        them as a spectator. If not specified, uses the current user. 

        Args: 

        name (str): Display name of the player
        status (str): Status of the player
        """
        if user_id is None:
            user_id = self.user_id
        if user_id is None:
            raise ValueError("No user_id provided and none set")

        player_details = UpdatePlayerEvent(
            id=str(user_id),
            name=name,
            status=status,
        )
        ui_event = UIEvent(type=UIEventType.UPDATE_PLAYER, payload=player_details)

        with session_scope() as session:
            new_player_event = GameEvent(
                game_id=self.game_id,
                event_type=EventType.UPDATE_PLAYER,
                details=player_details.dict(),
            )
            new_player_GUI_event = GameEvent(
                game_id=self.game_id,
                event_type=EventType.GUI,
                public_visibility=True,
                details=ui_event.dict(),
            )

            session.add(new_player_event)
            session.add(new_player_GUI_event)

    def get_player_status(self, user_id):
        """Get the status of the requested player

        Returns:
            Tuple[str, str]: Name and current status of player
        """
        q = EventQueue(
            self.game_id,
            type_filter=EventType.UPDATE_PLAYER,
        )
        player_name = None
        status = None

        for rename_event in q.get_all_events():
            if rename_event.details['id'] == user_id:
                player_name = rename_event.details['name']
                status = rename_event.details['status']

        return player_name, status

    def join(self, name: str = None):
        """Join or rejoin a game using the current user's id

        Args:
            name (str): Name of the user. Use prexissting / generate a new one
            if not provided
        """

        print(f"User {self.user_id} joining now")

        if EventQueue(self.game_id).get_latest_event_id() == 0:
            self.create_game()

        preexisting_name, preexisting_state = self.get_player_status(self.user_id)

        if not preexisting_name:
            self.new_player(name)
        else:
            # Player is already in the game: get their state and, if a new name is not
            # provided, their name
            if preexisting_name:
                state = preexisting_state
                if not name:
                    name = preexisting_name

            # If the name and state we're about to save are already in the database,
            # don't bother
            if name == preexisting_name and state == preexisting_state:
                return

            self.set_player(name, state)

    def new_player(self, name: str = None):

        # If no name provided, generate one
        if not name:
            global words
            with open(NAMES_FILE, newline='') as f:
                words = list(line.rstrip() for line in f.readlines())
            name = " ".join([
                random.choice(words),
                random.choice(words)
            ]).title()

        print("Making new player {} = {}".format(self.user_id, name))

        self.set_player(name, "spectating")

    def start_game(self):
        role_details = {
            "title": "Started!",
            "day_text": '''
The game has started!

I should probably write some more things here. 
            '''.strip(),
            "night_text": "",
            "button_visible": False,
        }

        players = self.get_current_players()
        print(players)

        role_events = []
        for p in players:
            self.set_player(None, Stati.NORMAL, user_id=p)

        ui_event = UIEvent(type=UIEventType.SET_CONTROLS, payload=role_details)

        with session_scope() as session:
            session.add(GameEvent(
                game_id=self.game_id,
                event_type=EventType.GUI,
                public_visibility=True,
                details=ui_event.dict(),
            ))
            for e in role_events:
                session.add(e)

        players = self.get_current_players()
        print(players)

    def get_current_players(self):
        """Get a list of current players in the game, with their states and roles
        """
        q = EventQueue(self.game_id, type_filter=[EventType.UPDATE_PLAYER,
                                                  EventType.REMOVE_PLAYER,
                                                  EventType.SET_ROLE])

        players = {}
        for event in q.get_all_events():
            if event.event_type == EventType.UPDATE_PLAYER:
                d = UpdatePlayerEvent.parse_obj(event.details)
                if d.id not in players:
                    players[d.id] = {
                        'name': d.name,
                        'status': d.status,
                        'role': None,
                    }
                else:
                    if d.name:
                        players[d.id]["name"] = d.name
                    if d.status:
                        players[d.id]["status"] = d.status
            elif event.event_type == EventType.SET_ROLE:
                d = SetRoleEvent.parse_obj(event.details)
                players[d.id]["role"] = d.role
            elif event.event_type == EventType.REMOVE_PLAYER:
                d = RemovePlayerEvent.parse_obj(event.details)
                del players[d.id]

        return players

    def create_game(self):
        self.set_stage(GameStages.DAY)
        role_details = {
            "title": "Ready to start",
            "day_text": '''
The game will begin as soon as someone presses start.  

If anyone joins after they, they'll be a spectator until the game finishes. 
            '''.strip(),
            "night_text": "",
            "button_visible": True,
            "button_enabled": True,
            "button_text": "Vote to start game",
            "button_confirm_text": "Waiting for all players...",
            "button_submit_url": "start_game",
            "button_submit_person": None,
        }
        ui_event = UIEvent(type=UIEventType.SET_CONTROLS, payload=role_details)

        with session_scope() as session:
            session.add(GameEvent(
                game_id=self.game_id,
                event_type=EventType.GUI,
                public_visibility=True,
                details=ui_event.dict(),
            ))

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

    def send_chat_message(self, msg, is_strong=False, player_list=None):
        """Post a message in the chat log

        Args:
            msg (str): Message to post
            is_strong (bool, optional): Display with HTML <strong>? Defaults to
                                        False.
            player_list (List[UUID], optional): List of player IDs who can see the
                                        message. All players if None. 
        """

        msg_details = {
            "msg": msg,
            "isStrong": is_strong,
        }

        message_obj = UIEvent(type=UIEventType.CHAT_MESSAGE, payload=msg_details)

        with session_scope() as session:
            if player_list:
                player_db_objs = [
                    GameEventVisibility(user_id=id) for id in player_list
                ]
                session.add(GameEvent(
                    game_id=self.game_id,
                    event_type=EventType.GUI,
                    public_visibility=False,
                    users_with_visibility=player_db_objs,
                    details=message_obj.dict(),
                ))
            else:
                session.add(GameEvent(
                    game_id=self.game_id,
                    event_type=EventType.GUI,
                    public_visibility=True,
                    details=message_obj.dict(),
                ))

    def set_stage(self, new_stage: GameStages):
        with session_scope() as session:
            session.add(GameEvent(
                game_id=self.game_id,
                event_type=EventType.GUI,
                public_visibility=True,
                details=UIEvent(type=UIEventType.GAME_STAGE, payload={"stage": new_stage}).dict(),
            ))
