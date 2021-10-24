from typing import Optional
from uuid import UUID

from fastapi import Depends
from pydantic import constr

from core import settings
from core.models import client, VehicleInfo
from core.models.client import ActionType, ClientToken, AuditLog
from core.models.vehicle import VehicleType


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


def add_audit_log(action: ActionType):
    async def wrapper(
            vehicle_plate: constr(max_length=32, to_lower=True),
            vehicle_type: Optional[VehicleType] = None,
            _client: ClientToken = Depends(get_current_client),
    ) -> AuditLog:
        vehicle_info, _ = await VehicleInfo.get_or_create(plate=vehicle_plate)
        if vehicle_type is not None:
            vehicle_info.type = vehicle_type
            await vehicle_info.save()
        return await AuditLog.create(belongs_to=_client, action=action, related_to=vehicle_info)
    return wrapper
