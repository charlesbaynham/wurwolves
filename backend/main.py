import hashlib
import os
import random
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Path, Query
from sqlalchemy import and_, or_

from .events import EventQueue
from .model import EventType, GameEvent
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
    return EventQueue(game_id, user_ID=UUID(user_ID)).get_all_events(since=since)


@router.get("/{game_id}/newest_id")
async def get_newest_timestamp(
        game_id: str = Path(..., title="The four-word ID of the game"),
        user_ID=Depends(get_user_id)
):
    return EventQueue(game_id, user_ID=UUID(user_ID)).get_latest_event_id()


@router.get("/{game_id}/get_secrets")
async def get_secrets(
        game_id: str = Path(..., title="The four-word ID of the game"),
        since: int = Query(None, title="If provided, only show events with larger IDs that this"),
):
    return EventQueue(game_id, public_only=False).get_all_events(since=since)


# @router.get("/api/{game_id}/new_player")
# async def make_new_player(
#     game_id: str = Path(...,
#                         title="The four-word ID of the game"),
#     player_name: str = Query(..., title="Display name of the new player"),
#     user_ID=Depends(get_user_id),
# ):
#     with session_scope() as session:
#         session.add(GameEvent(
#             game_id=hash_game_id(game_id), event_type=EventType.GUI,
#             details={
#                 "type": "new_user",
#                 "id": user_ID,
#                 "name": player_name,
#                 "status": "spectating",
#             }, public_visibility=True,
#         ))


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
