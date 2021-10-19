from uuid import UUID

from pydantic import constr

from core import settings
from core.models import client


async def get_current_client(
        uuid: UUID,
        token: constr(min_length=128, max_length=128),
) -> client.ClientToken:
    return await client.authenticate(uuid, token)


class InvalidTokenError(Exception):
    pass


async def require_admin_token(
        token: str
) -> bool:
    if token != settings.ADMIN_TOKEN:
        raise InvalidTokenError()
    return True
