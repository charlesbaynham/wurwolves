import hashlib
import os
import random
from datetime import datetime

from fastapi import Depends, FastAPI, Path, Query
from sqlalchemy import and_, or_

from .model import EventType, GameEvent
from .user_id import get_user_id

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')
words = None
data = {}

app = FastAPI()


@app.get("/api/{game_id}/ui_events")
async def ui_events(
        game_id: str = Path(..., title="The four-word ID of the game"),
        user_ID=Depends(get_user_id)
):
    with session_scope() as session:
        # events = session.query(GameEvent).all()
        events = session.query(GameEvent.created).filter_by(
            game_id=hash_string(game_id)).order_by(GameEvent.id.desc()).first()

        return [e for e in events]


@app.get("/api/{game_id}/newest_timestamp")
async def get_newest_timestamp(
        game_id: str = Path(..., title="The four-word ID of the game"),
        user_ID=Depends(get_user_id)
):
    with session_scope() as session:
        newest_timestamp = session.query(GameEvent.created).filter(
            GameEvent.game_id == hash_string(game_id)).first()

        return newest_timestamp


@app.get("/api/{game_id}/new_player")
async def make_new_player(
    game_id: str = Path(...,
                        title="The four-word ID of the game"),
    player_name: str = Query(..., title="Display name of the new player"),
    user_ID=Depends(get_user_id),
):
    with session_scope() as session:
        session.add(GameEvent(
            game_id=hash_string(game_id), event_type=EventType.GUI,
            details={
                "type": "new_user",
                "id": user_ID,
                "name": player_name,
                "status": "spectating",
            }, public_visibility=True,
        ))


@ app.get("/api/log_connection/")
async def log_connection(*, user_ID=Depends(get_user_id)):
    time_str = datetime.now().isoformat()
    data[user_ID] = time_str
    return data


@ app.get("/api/get_game/")
async def get_game():
    global words
    if not words:
        with open(WORDS_FILE, newline='') as f:
            words = list(line.rstrip() for line in f.readlines())

    return '-'.join([
        random.choice(words),
        random.choice(words),
        random.choice(words),
        random.choice(words),
    ])


def hash_string(text: str):
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
