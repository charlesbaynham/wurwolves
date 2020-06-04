from datetime import datetime

from fastapi import Depends, FastAPI

from .user_id import user_id

app = FastAPI()

data = {}


@app.get("/api/hello/")
async def read_stuff():
    return "Hello world!"

@app.get("/")
async def main():
    return "The default response"


@app.get("/api/stuff/")
async def read_stuff(*, user_ID=Depends(user_id)):
    return str(user_ID)


@app.get("/api/log_connection/")
async def log_connection(*, user_ID=Depends(user_id)):
    time_str = datetime.now().isoformat()
    data[user_ID] = time_str
    return data
