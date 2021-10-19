from uuid import UUID

from pydantic import constr

from core import settings
from core.models.client import authenticate, ClientToken


async def get_current_client(
        uuid: UUID,
        token: constr(min_length=128, max_length=128),
) -> ClientToken:
    return await authenticate(uuid, token)


class InvalidTokenError(Exception):
    pass


async def require_token(
        token: str
) -> bool:
    if token != settings.ADMIN_TOKEN:
        raise InvalidTokenError()
    return True
