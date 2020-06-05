import os
import random
from datetime import datetime

from fastapi import Depends, FastAPI

from .user_id import user_id

WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')
words = None
data = {}

app = FastAPI()


@app.get("/api/hello/")
async def read_stuff():
    return "Hello world!"


@app.get("/api/stuff/")
async def read_stuff(*, user_ID=Depends(user_id)):
    return str(user_ID)


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
            words = list(l.rstrip() for l in f.readlines())

    return '-'.join([
        random.choice(words),
        random.choice(words),
        random.choice(words),
        random.choice(words),
    ])
