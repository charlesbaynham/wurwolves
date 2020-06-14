import asyncio
import logging
import os
import random

from fastapi import APIRouter, Depends, FastAPI, Path, Query, HTTPException

from . import frontend_parser
from .database import session_scope
from .game import WurwolvesGame
from .model import User
from .user_id import get_user_id

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')

words = None

app = FastAPI()
router = APIRouter()


@router.get("/{game_tag}/state")
def get_state(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id)
):
    state = frontend_parser.parse_game_to_state(game_tag, user_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Game '{game_tag}' not found")
    return state


@router.get("/{game_tag}/state_hash")
async def get_state_hash(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    known_hash: int = Query(0, title="The most recent known hash of the client. If provided, this call will block until a change occurs"),
    user_id=Depends(get_user_id)
):
    """
    Get a string which identifies the state of the state.

    Basically a hash: this string is guaranteed to change if the state changes
    """
    return await WurwolvesGame(game_tag).get_hash(known_hash=known_hash)


@router.post("/{game_tag}/start_game")
async def start_game(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id)
):
    """
    Vote to start the game (actually just starts it right now)
    """
    WurwolvesGame(game_tag).start_game()


@router.post("/{game_tag}/join")
async def join(
        game_tag: str = Path(..., title="The four-word ID of the game"),
        user_id=Depends(get_user_id)
):
    WurwolvesGame(game_tag).join(user_id)


@router.post("/set_name")
async def set_name(
    name: str = Query(..., title="New username. This will be used in all games for this user"),
    user_id=Depends(get_user_id)
):
    WurwolvesGame.set_user_name(user_id, name)


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
