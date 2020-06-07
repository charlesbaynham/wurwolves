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
NAMES_FILE = os.path.join(os.path.dirname(__file__), 'names.txt')
words = None
names = None

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

    out = [{
        "id": id, "details": event.dict()
    } for id, event in events.items()]
    return out


@router.get("/{game_id}/chat")
async def get_chat(
    game_id: str = Path(..., title="The four-word ID of the game"),
    since: int = Query(None, title="If provided, only show events with larger IDs that this"),
    user_ID=Depends(get_user_id),
):
    events = EventQueue(
        game_id,
        user_ID=UUID(user_ID),
        type_filter=EventType.CHAT,
    ).get_all_events(since=since)

    return events


@router.post("/{game_id}/join")
async def join(
        game_id: str = Path(..., title="The four-word ID of the game"),
        name: str = Query(None, title="The player's name"),
        user_id=Depends(get_user_id)
):
    game = WurwolvesGame(game_id, user_id)
    state = "spectating"

    print(f"User {user_id} joining now")

    preexisting_name, preexisting_state = game.get_player_status(user_id)

    # If the player is already in the game, get their state and possibly their name
    if preexisting_name:
        state = preexisting_state
        if not name:
            name = preexisting_name

    # If the player isn't in the game and doesn't yet have a name, generate one
    if not preexisting_name and not name:
        global words
        with open(NAMES_FILE, newline='') as f:
            words = list(line.rstrip() for line in f.readlines())
        name = " ".join([
            random.choice(words),
            random.choice(words)
        ]).title()

    # If the name and state we're about to save are already in the database,
    # don't bother
    if name == preexisting_name and state == preexisting_state:
        return

    game.set_player(name, state)


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
