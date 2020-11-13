from threading import RLock
from uuid import UUID
from uuid import uuid4 as get_uuid

from fastapi import Cookie
from fastapi import Request
from fastapi import Response

no_cookie_clients = {}
no_cookie_lock = RLock()


async def get_user_id(
    *,
    response: Response,
    session_UUID: str = Cookie(None, title="A UUID generated for each user session"),
    request: Request,
):
    ip = request.client.host

    if session_UUID is None:
        parsed_uuid = assign_new_ID(response, ip)
    else:
        if ip in no_cookie_clients:
            del no_cookie_clients[ip]

        try:
            parsed_uuid = UUID(session_UUID)
        except ValueError:
            parsed_uuid = assign_new_ID(response, ip)

    return parsed_uuid


def assign_new_ID(response, ip) -> UUID:
    # If there isn't yet a session cookie, we have to be careful: there
    # might be concurrent requests from this cookieless session and they all
    # need to receive the same cookie otherwise things get duplicated. To
    # achieve this, we'll maintain a dict of ip -> uuid which is only
    # accessed if there's no session id. If a user joins without a cookie,
    # we store their uuid in the dict. Any other requests from their IP with
    # no cookie are given the same uuid. Once a request arrives from this ip
    # which has a cookie, delete them from the dict.
    with no_cookie_lock:
        if ip in no_cookie_clients:
            session_UUID = no_cookie_clients[ip]
        else:
            session_UUID = get_uuid()
            no_cookie_clients[ip] = session_UUID

    response.set_cookie(key="session_UUID", value=session_UUID)

    return session_UUID
