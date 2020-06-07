'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
import os
import random
from uuid import UUID

from .database import session_scope
from .events import EventQueue, UIEvent, UIEventType
from .model import EventType, GameEvent, hash_game_id

NAMES_FILE = os.path.join(os.path.dirname(__file__), 'names.txt')
names = None


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
        them as a spectator. If not speecified, uses the current user. 

        Args: 

        name (str): Display name of the player
        status (str): Status of the player
        """
        if user_id is None:
            user_id = self.user_id
        if user_id is None:
            raise ValueError("No user_id provided and none set")

        player_details = {
            "id": str(user_id),
            "name": name,
            "status": status,
        }
        ui_event = UIEvent(type=UIEventType.UPDATE_PLAYER, payload=player_details)

        with session_scope() as session:
            new_player_event = GameEvent(
                game_id=self.game_id,
                event_type=EventType.UPDATE_PLAYER,
                details=player_details,
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

        self.set_player(name, "spectating")

    def create_game(self):
        role_details = {
            "name": "",
            "day_text": "",
            "night_text": "",
            "button_visible": False,
            "button_enabled": False,
            "button_text": "",
            "button_confirm_text": "",
        }
        # ui_event = UIEvent(type=UIEventType.UPDATE_PLAYER, payload=player_details)

        # with session_scope() as session:
        #     new_player_event = GameEvent(
        #         game_id=self.game_id,
        #         event_type=EventType.UPDATE_PLAYER,
        #         details=player_details,
        #     )
        #     new_player_GUI_event = GameEvent(
        #         game_id=self.game_id,
        #         event_type=EventType.GUI,
        #         public_visibility=True,
        #         details=ui_event.dict(),
        #     )

        #     session.add(new_player_event)
        #     session.add(new_player_GUI_event)
