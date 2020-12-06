import logging
import os
import random
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from fastapi import Request
from fastapi import Response
from starlette.middleware.sessions import SessionMiddleware

from . import frontend_parser
from .game import WurwolvesGame
from .roles import router as roles_router
from .user_id import get_user_id

logging.getLogger().setLevel(logging.INFO)

WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.txt")

words = None

app = FastAPI()
router = APIRouter()

app.add_middleware(
    SessionMiddleware, secret_key="james will never understand the prostitute"
)


@router.get("/{game_tag}/state")
def get_state(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
):
    state = frontend_parser.parse_game_to_state(game_tag, user_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Game '{game_tag}' not found")
    return state


@router.post("/{game_tag}/chat")
def send_chat(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
    message: str = Query(..., description="Chat message for secret chat"),
):
    WurwolvesGame(game_tag).send_secret_message(user_id, message)


@router.get("/{game_tag}/state_hash")
async def get_state_hash(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    known_hash: int = Query(
        0,
        title="The most recent known hash of the client. If provided, this call will block until a change occurs",
    ),
    user_id=Depends(get_user_id),
):
    """
    Get a string which identifies the state of the state.

    Basically a hash: this string is guaranteed to change if the state changes
    """
    game = WurwolvesGame(game_tag)
    game.player_keepalive(user_id)
    return await game.get_hash(known_hash=known_hash)


@router.post("/{game_tag}/join")
async def join(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
):
    WurwolvesGame(game_tag).join(user_id)


@router.post("/{game_tag}/end_game")
async def end_game(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
):
    g = WurwolvesGame(game_tag)
    user_name = g.get_user_model(user_id).name
    g.send_chat_message(f"The game was ended early by {user_name}", is_strong=True)
    g.end_game()


@router.post("/set_name")
async def set_name(
    name: str = Query(
        ..., title="New username. This will be used in all games for this user"
    ),
    user_id=Depends(get_user_id),
):
    WurwolvesGame.set_user_name(user_id, name)


@router.get("/my_id")
async def get_id(*, user_ID=Depends(get_user_id)):
    return user_ID


@router.get("/get_game")
async def get_game():
    global words
    if not words:
        with open(WORDS_FILE, newline="") as f:
            words = list(line.rstrip() for line in f.readlines())

    return "-".join(
        [
            random.choice(words),
            random.choice(words),
            random.choice(words),
            random.choice(words),
        ]
    )


@router.get("/hello")
def hello():
    return {"msg": "Hello world!"}


app.include_router(router, prefix="/api")
app.include_router(roles_router, prefix="/api")
