'''
Game module

This module provides the Game class, for interacting with a single game
'''

import hashlib


class WurwolvesGame:
    """
    Provides methods for accessing all the properties of a wurwolves game. This
    object is initialised with the ID of a game and loads all other information
    from the database on request.

    The data describing a game is stored as a series of events in an event log.
    To recover the state of a game, the server therefore replays all events in
    the log from start to end. See the :class:`backend.model.GameEvent` for more
    information.
    """

    def __init__(self, game_id: str):
        self.id = self.hash_string(game_id)
        self.latest_event_id = None

    def update_state(self):
        """
        Update the state of this object

        Access the database to retrieve any events relating to this game which
        have not yet been parsed. Parse them all in order, updating this object
        the way. 
        """        
        pass

    @staticmethod
    def hash_string(text: str, N: int = 4):
        """ Hash a string into an N-byte integer

        This method is used to convert the four-word style game identifiers into
        a database-friendly integer. 
        """

        hash_obj = hashlib.md5(text.encode())
        hash_bytes = list(hash_obj.digest())

        # Slice off the first N bytes and cast to integer
        return int.from_bytes(hash_bytes[0:N], 'big')
