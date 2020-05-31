from datetime import datetime
from uuid import uuid4 as get_uuid

from fastapi import Cookie, Depends, FastAPI, Response

app = FastAPI()

data = {}


@app.get("/items/")
async def user_id(*, response: Response, session_UUID: str = Cookie(None)):
    if session_UUID is None:
        new_val = get_uuid()
        session_UUID = new_val
        response.set_cookie(key="session_UUID", value=new_val)
    return session_UUID


@app.get("/stuff/")
async def read_stuff(*, user_ID=Depends(user_id)):
    return str(user_ID)


@app.get("/log_connection/")
async def log_connection(*, user_ID=Depends(user_id)):
    time_str = datetime.now().isoformat()
    data[user_ID] = time_str
    return data
