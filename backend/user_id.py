from uuid import uuid4 as get_uuid

from fastapi import Cookie, Response


async def get_user_id(*,
                  response: Response,
                  session_UUID: str = Cookie(
                      None, title="A UUID generated for each user session")
                  ):
    if session_UUID is None:
        new_val = get_uuid()
        session_UUID = new_val
        response.set_cookie(key="session_UUID", value=new_val)
    return str(session_UUID)
