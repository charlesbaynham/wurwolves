import os
import random

from fastapi import APIRouter, Depends, FastAPI, Path

# from .frontend_parser import FrontendState
from .game import WurwolvesGame
from .user_id import get_user_id
from . import frontend_parser

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')

words = None

app = FastAPI()
router = APIRouter()


@router.get("/{game_tag}/state")
def get_state(
    game_tag: str = Path(..., title="The four-word ID of the game"),
    user_id=Depends(get_user_id)
):  
    return frontend_parser.parse_game_to_state(game_tag, user_id)


@router.get("/{game_tag}/start_game")
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
