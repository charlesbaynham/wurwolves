import os
import random
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Path, Query
from pydantic import BaseModel

from .game import WurwolvesGame
from .user_id import get_user_id

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')

words = None

app = FastAPI()
router = APIRouter()


# @router.get("/{game_id}/ui_events")
# async def ui_events(
#         game_id: str = Path(..., title="The four-word ID of the game"),
#         since: int = Query(None, title="If provided, only show events with larger IDs that this"),
#         user_ID=Depends(get_user_id)
# ):
#     events = EventQueue(
#         game_id,
#         user_ID=UUID(user_ID),
#         type_filter=EventType.GUI,
#     ).get_all_UI_events(since=since)

#     out = [{
#         "id": id, "details": event.dict()
#     } for id, event in events.items()]
#     return out


@router.get("/{game_id}/start_game")
async def start_game(
    game_id: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id)
):
    """
    Vote to start the game (actually just starts it right now)
    """
    WurwolvesGame(game_id).start_game()


# @router.get("/{game_id}/chat")
# async def get_chat(
#     game_id: str = Path(..., title="The four-word ID of the game"),
#     since: int = Query(None, title="If provided, only show events with larger IDs that this"),
#     user_id=Depends(get_user_id),
# ):
#     events = EventQueue(
#         game_id,
#         user_ID=UUID(user_id),
#         type_filter=EventType.CHAT,
#     ).get_all_events(since=since)

#     return events


@router.post("/{game_id}/join")
async def join(
        game_id: str = Path(..., title="The four-word ID of the game"),
        user_id=Depends(get_user_id)
):
    WurwolvesGame(game_id).join(user_id)


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
