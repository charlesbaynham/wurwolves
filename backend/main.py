from uuid import uuid4 as get_uuid

from fastapi import Cookie, FastAPI, Response

app = FastAPI()


@app.get("/items/")
async def read_items(*, response: Response, fakesession: str = Cookie(None)):
    if fakesession is None:
        new_val = get_uuid()
        fakesession = new_val
        response.set_cookie(key="fakesession", value=new_val)
    return {"fakesession": fakesession}
