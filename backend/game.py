'''
Game module

This module provides the WurwolvesGame class, for interacting with a single game
'''
from uuid import UUID

from .database import session_scope
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

    # def update_state(self):
    #     """
    #     Update the state of this object

    #     Access the database to retrieve any events relating to this game which
    #     have not yet been parsed. Parse them all in order, updating this object
    #     the way.
    #     """
    #     pass

    def add_player(self, name: str):
        """Add this player to the game

        Add's a player with the current user's ID to the game as a spectator. 

        Args:
            name (str): Display name of the player
        """
        player_details = {
            "id": str(self.user_id),
            "name": name,
            "status": "spectating",
        }

        with session_scope() as session:
            new_player_event = GameEvent(
                game_id=self.game_id,
                event_type=EventType.NEW_PLAYER,
                details=player_details
            )
            new_player_GUI_event = GameEvent(
                game_id=self.game_id,
                event_type=EventType.GUI,
                public_visibility=True,
                details=player_details
            )

            session.add(new_player_event)
            session.add(new_player_GUI_event)
