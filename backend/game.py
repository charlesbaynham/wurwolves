'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
from uuid import UUID

from .database import session_scope
from .events import UIEvent, UIEventType
from .model import EventType, GameEvent, hash_game_id


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

    Note that :mod:`backend.events` does not provide methods for altering the
    queue. This is intentional: all write access is performed through this
    module instead.     
    """

    def __init__(self, game_id: str, user_id: UUID):
        self.game_id = hash_game_id(game_id)
        self.user_id = user_id
        self.latest_event_id = None

    def set_player(self, name: str, status: str):
        """
        Update this player's name and status

        Updates this player's state in the game. If not already present, adds
        them as a spectator. 

        Args: 

        name (str): Display name of the player
        status (str): Status of the player
        """
        player_details = {
            "id": str(self.user_id),
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
