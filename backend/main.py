import json
import logging
import os
import random
from typing import Optional

import psutil
import pydantic
from dotenv import find_dotenv
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from fastapi import Request
from fastapi import Response
from starlette.middleware.sessions import SessionMiddleware

from .game import WurwolvesGame
from .model import DistributionSettings
from .roles import RANDOMISED_ROLES
from .roles import router as roles_router
from .user_id import get_user_id

logger = logging.getLogger("main")

# Set the root logger level to LOG_LEVEL if specified
load_dotenv(find_dotenv())
if "LOG_LEVEL" in os.environ:
    logging.getLogger().setLevel(os.environ.get("LOG_LEVEL"))
    logger.info("Setting log level to %s", os.environ.get("LOG_LEVEL"))
else:
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Setting log level to INFO by default")

WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.txt")

words = None

app = FastAPI()
router = APIRouter()

app.add_middleware(
    SessionMiddleware,
    secret_key="james will never understand the prostitute",
    max_age=60 * 60 * 24 * 365 * 10,
)


def get_mem_usage():
    return psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2


@router.get("/{game_tag}/state")
async def get_state(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Starting get_state for UUID %s", user_id)
        logger.debug("get_state memory usage = %.0f MB", get_mem_usage())

    state = WurwolvesGame(game_tag).parse_game_to_state(user_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Game '{game_tag}' not found")
    return state


@router.get("/default_role_weights")
async def get_default_role_weights():
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Starting get_default_role_weights")

    return {k.value: v for k, v in RANDOMISED_ROLES.items()}


@router.get("/{game_tag}/game_config_mode")
async def get_game_config_mode(
    game_tag: str = Path(..., title="The four-word ID of the game"),
):
    logger.info("Starting get_game_config for %s", game_tag)

    return WurwolvesGame(game_tag).get_game_config_mode()


@router.post("/{game_tag}/game_config_mode")
async def set_game_config_mode(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    new_config_mode: str = Query(
        ...,
        title="New game mode. Must be easy, medium or hard",
    ),
):
    logger.info(
        "Starting set_game_config_mode for game %s, state %s", game_tag, new_config_mode
    )
    WurwolvesGame(game_tag).set_game_config_mode(new_config_mode.lower())


@router.post("/{game_tag}/chat")
def send_chat(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
    message: str = Query(..., description="Chat message for secret chat"),
):
    logger.debug("Starting send_chat for UUID %s", user_id)

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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Starting get_state_hash for UUID %s", user_id)
        logger.debug("get_state_hash memory usage = %.0f MB", get_mem_usage())

    game = WurwolvesGame(game_tag)
    game.player_keepalive(user_id)
    return await game.get_hash(known_hash=known_hash)


@router.post("/{game_tag}/join")
async def join(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
):
    logger.debug("Starting join for UUID %s", user_id)

    WurwolvesGame(game_tag).join(user_id)


@router.post("/{game_tag}/end_game")
async def end_game(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id),
):
    logger.debug("Starting end_game for UUID %s", user_id)

    g = WurwolvesGame(game_tag)
    user_name = g.get_user_name(user_id)
    g.send_chat_message(f"The game was ended early by {user_name}", is_strong=True)
    g.end_game()


@router.post("/set_name")
async def set_name(
    name: str = Query(
        ..., title="New username. This will be used in all games for this user"
    ),
    user_id=Depends(get_user_id),
):
    logger.debug("Starting set_name for UUID %s", user_id)

    WurwolvesGame.set_user_name(user_id, name)


@router.get("/my_id")
async def get_id(*, user_id=Depends(get_user_id)):
    logger.debug("Starting get_id for UUID %s", user_id)

    return user_id


@router.get("/get_game")
async def get_game():
    logger.debug("Starting get_game")

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
