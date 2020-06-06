import hashlib
import os
import random
from datetime import datetime

from fastapi import Depends, FastAPI, Path

from .database import session_scope
from .model import EventType, GameEvent
from .user_id import user_id

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')
words = None
data = {}

app = FastAPI()


@app.get("/api/{game_id}/ui_events")
async def ui_events(
        game_id: str = Path(..., title="The four-word ID of the game"),
        user_ID=Depends(user_id)
):
    with session_scope() as session:
        # events = session.query(GameEvent).all()
        events = session.query(GameEvent.created, GameEvent.id).filter(
            GameEvent.game_id == hash_string(game_id)).all()
        return events


@app.get("/api/{game_id}/new")
async def read_stuff(
    game_id: str = Path(...,
                        title="The four-word ID of the game"),
    user_ID=Depends(user_id),
):
    with session_scope() as session:
        session.add(GameEvent(
            game_id=hash_string(game_id), event_type=EventType.GUI,
            details={"user_id": user_ID}, public_visibility=True,
        ))


@app.get("/api/log_connection/")
async def log_connection(*, user_ID=Depends(user_id)):
    time_str = datetime.now().isoformat()
    data[user_ID] = time_str
    return data


@app.get("/api/get_game/")
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
