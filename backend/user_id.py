import logging
from threading import RLock
from uuid import UUID
from uuid import uuid4 as get_uuid

from fastapi import Cookie
from fastapi import Query
from fastapi import Request
from fastapi import Response

no_cookie_clients = {}
no_cookie_lock = RLock()


async def get_user_id(
    *,
    response: Response,
    temporary_id: float = Query(
        0,
        title="A temporary ID used to identify clients before a cookie is set. Ignored if a cookie already exists",
    ),
    request: Request,
):
    if not temporary_id:
        temporary_id = request.client.host

    try:
        session_UUID = request.session["UUID"]
    except KeyError:
        session_UUID = None

    if session_UUID is None:
        parsed_uuid = assign_new_ID(request, temporary_id)
        logging.info(
            "Blank client, tempID %s, assigned UUID %s", temporary_id, parsed_uuid
        )
    else:
        if temporary_id in no_cookie_clients:
            logging.info(
                "tempID %s responded with UUID %s. Deleting from dict",
                temporary_id,
                session_UUID,
            )
            del no_cookie_clients[temporary_id]

        try:
            parsed_uuid = UUID(session_UUID)
        except ValueError:
            parsed_uuid = assign_new_ID(request, temporary_id)
            logging.error(
                "Error parsing UUID %s from tempID %s. Reassiging as %s",
                session_UUID,
                temporary_id,
                parsed_uuid,
            )

    return parsed_uuid


def assign_new_ID(request: Request, temp_id) -> UUID:
    # If there isn't yet a session cookie, we have to be careful: there
    # might be concurrent requests from this cookieless session and they all
    # need to receive the same cookie otherwise things get duplicated. To
    # achieve this, we'll maintain a dict of temp_id -> uuid which is only
    # accessed if there's no session id. If a user joins without a cookie,
    # we store their uuid in the dict. Any other requests from their temp_id with
    # no cookie are given the same uuid. Once a request arrives from this temp_id
    # which has a cookie, delete them from the dict.
    with no_cookie_lock:
        if temp_id in no_cookie_clients:
            session_UUID = no_cookie_clients[temp_id]
        else:
            session_UUID = get_uuid()
            no_cookie_clients[temp_id] = session_UUID

    request.session["UUID"] = str(session_UUID)

    return session_UUID
