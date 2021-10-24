from fastapi import APIRouter, Depends

from core.dependencies import get_current_client, add_audit_log
from core.models import ClientToken, AuditLog
from core.models.client import ActionType
from core.models.vehicle import add_entry_log, EntryLogSchemaLite, add_leave_log

router = APIRouter(prefix='/client', tags=['门岗客户端'])


@router.put('/entry', description='载具进场', response_model=EntryLogSchemaLite, status_code=201)
async def vehicle(
        audit_log: AuditLog = Depends(add_audit_log(ActionType.VEHICLE_ENTRY)),
):
    return await EntryLogSchemaLite.from_tortoise_orm(await add_entry_log(audit_log.related_to))


@router.delete(
    '/entry',
    description='载具离场 如需要支付则将EntryLog的id传入支付接口',
    response_model=EntryLogSchemaLite,
    status_code=200
)
async def vehicle(
        audit_log: AuditLog = Depends(add_audit_log(ActionType.VEHICLE_LEAVE)),
):
    return await EntryLogSchemaLite.from_tortoise_orm(await add_leave_log(audit_log.related_to))


@router.put('/entry', description='生成订单')
async def order(
        audit_log: AuditLog = Depends(add_audit_log(ActionType.GENERATE_ORDER)),
):
    # TODO
    return
