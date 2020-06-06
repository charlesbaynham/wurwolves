import os
import random
from datetime import datetime

from fastapi import Depends, FastAPI, Path

from .database import session_scope
from .user_id import user_id
from .model import GameEvent, EventType


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
        events = session.query(GameEvent.game_id, GameEvent.event_type).all()
        return events


@app.get("/api/stuff/")
async def read_stuff(*, user_ID=Depends(user_id)):
    with session_scope() as session:
        session.add(GameEvent(
            game_id=123, event_type=EventType.GUI,
            details={"user_id": user_ID}, public_visibility=True
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
