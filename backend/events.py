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

from sqlalchemy import or_
from sqlalchemy.orm import Query

from .database import session_scope
from .model import GameEvent, hash_game_id


class EventQueue:
    def __init__(
        self,
        game_id: str,
        public_only=True,
        user_ID: UUID = None,
    ):
        """Accesses a queue of GameEvents from the database, applying visibility filters

            By default, access all events relating to a game. Optionally filters can
            be applied to limit the items returned by this object. 

            Args: 

                game_id (str):  The ID of the game to check for. Note that this is the string
                                seen by the user and will be hashed by
                                :meth:`backend.game.WurwolvesGame.hash_game_id`

                public_only (bool, optional):   Should this queue only return public events?
                                                Defaults to True. Ignored if user_ID is provided. 

                user_ID (UUID, optional):   If present, only return events visible to
                                            this user (including public events). Defaults to None.
        """
        self.game_id = hash_game_id(game_id)
        self.public_only = public_only
        self.user_ID = user_ID

    def filter_query(self, query: Query):
        query = query.filter_by(game_id=self.game_id)

        if self.user_ID:
            query = query.filter(or_(
                GameEvent.public_visibility,
                GameEvent.users_with_visibility.any(user_id=self.user_ID)                
            ))
        elif self.public_only:
            query = query.filter_by(public_visibility=True)

        return query

    def get_latest_event_id(self):
        """
        Gets the id of the latest game event applicable to this game

        Event IDs are guaranteed to be in ascending order, so user code can
        check if their event queue is up to date by comparing the latest event
        ID they have processed against the one returned from this function. 

        This method applies the filters set up on this object during initiaion. 

        Returns: 
            int: ID of the newest GameEvent that matches the filters set on
            this object. 
        """
        with session_scope() as session:
            newest_id = self.filter_query(
                session
                .query(GameEvent.id)
                .order_by(GameEvent.id.desc())
            ).first()

        return newest_id[0]

    def get_all_events(self, since=None):
        """Get all events for this game

        This method applies the filters set up on this object during initiaion. 

        Args:
            since (int, optional): Only return events with IDs greater than this. Defaults to None.

        Returns:
            List[GameEvent]: A chronological list of all GameEvents for this game
        """
        with session_scope() as session:
            q = self.filter_query(
                session
                .query(GameEvent.id, GameEvent.event_type, GameEvent.details)
                .order_by(GameEvent.id.asc())
            )

            if since:
                q = q.filter(GameEvent.id > since)

            return q.all()
