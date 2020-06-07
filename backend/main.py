import os
import random
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Path, Query
from pydantic import BaseModel

from .events import EventQueue, UIEvent
from .game import WurwolvesGame
from .model import EventType
from .user_id import get_user_id

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')
words = None
data = {}

app = FastAPI()
router = APIRouter()


@router.get("/{game_id}/ui_events")
async def ui_events(
        game_id: str = Path(..., title="The four-word ID of the game"),
        since: int = Query(None, title="If provided, only show events with larger IDs that this"),
        user_ID=Depends(get_user_id)
):
    events = EventQueue(
        game_id,
        user_ID=UUID(user_ID),
        type_filter=EventType.GUI,
    ).get_all_UI_events(since=since)

    events = [{
        "id": id, "event": event.dict()
    } for id, event in events.items()]
    return events


@router.post("/{game_id}/join_game")
async def join_game(
        game_id: str = Path(..., title="The four-word ID of the game"),
        name: str = Query(..., title="The player's name"),
        user_ID=Depends(get_user_id)
):
    WurwolvesGame(game_id, user_ID).set_player(name)


@router.get("/{game_id}/newest_id")
async def get_newest_timestamp(
        game_id: str = Path(..., title="The four-word ID of the game"),
        user_ID=Depends(get_user_id)
):
    return EventQueue(
        game_id,
        user_ID=UUID(user_ID),
        type_filter=EventType.GUI,
    ).get_latest_event_id()


@router.get("/{game_id}/get_secrets")
async def get_secrets(
        game_id: str = Path(..., title="The four-word ID of the game"),
        since: int = Query(None, title="If provided, only show events with larger IDs that this"),
):
    return EventQueue(game_id, public_only=False).get_all_events(since=since)


@router.get("/my_id")
async def get_id(*, user_ID=Depends(get_user_id)):
    return user_ID


@router.get("/get_game")
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


@router.get('/hello')
def hello():
    return {
        "msg": "Hello world!"
    }


app.include_router(router, prefix='/api')
