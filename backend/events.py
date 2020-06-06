'''
This module contains all the code related to retrieving and manipulating the
event log. Note that the actual description of the database schema is not here,
it's stored in :modu:`backend.model`. 

This module is responsible for accessing the list of events, handling client
requests for accessing the applicable subset of events visible to a particular
user and updating the event log with new events. Note that the clients never
directly send updates to the event log: clients can request read access to the
events, but cannot write to them. To effect a change, clients must send a
request to the :modu:`backend.game` module which will evaluate their request and
may perform updates to the event log in response. 
'''
from uuid import UUID

from .database import session_scope
from .model import GameEvent


class EventQueue:
    def __init__(
        self,
        game_id: int,
        public_only=False,
        user_ID: UUID = None,
    ):
        """Make an EventQueue, applying visibility filters

        By default, access all events relating to a game. Optionally filters can
        be applied to limit the items returned by this object. 

        Args: 

            game_id (int): ID of the game to get events for. Required. 

            public_only (bool, optional):   Should this queue only return public events?
                                            Defaults to False.

            user_ID (UUID, optional):   If present, only return events visible to
                                        this user (including public events). Defaults to None.
        """       
        pass

    def get_latest_event_id(game_id: int):
        """Gets the id of the latest game event applicable to this game

        Event IDs are guaranteed to be in ascending order, so user code can
        check if their event queue is up to date by comparing the latest event
        ID they have processed against the one returned from this function. 

        This method applies the filters set up on this object during initiaion. 

        Args: game_id (int): The ID of the game to check for. Note that this is
            the integer id not the string seen by the user. This comes from
            :meth:`backend.game.WurwolvesGame.hash_string`

        Returns: int: ID of the newest GameEvent that matches the filters set on
        this object. 
        """
        with session_scope() as session:
            newest_timestamp = session.query(GameEvent.created).filter(
                GameEvent.game_id == hash_string(game_id)).first()

            return newest_timestamp
