from typing import List, Dict

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import ValidationError, BaseModel, parse_obj_as

from core.conf import settings
from core.dependencies import get_current_client, add_audit_log
from core.models import ClientToken, AuditLog, FeeRecordSchema
from core.models.client import ActionType
from core.models.vehicle import add_entry_log, EntryLogSchemaLite, add_leave_log, generate_fee_record, FeeRecord

router = APIRouter(prefix='/client', tags=['门岗客户端'])


@router.put('/entry', description='载具进场', response_model=EntryLogSchemaLite, status_code=201)
async def vehicle(
        audit_log: AuditLog = Depends(add_audit_log(ActionType.VEHICLE_ENTRY)),
):
    return await EntryLogSchemaLite.from_tortoise_orm(await add_entry_log((await audit_log.related_to).plate))


@router.delete(
    '/entry',
    description='载具离场 如需要支付则将EntryLog的id传入支付接口',
    response_model=EntryLogSchemaLite,
    status_code=200
)
async def vehicle(
        audit_log: AuditLog = Depends(add_audit_log(ActionType.VEHICLE_LEAVE)),
):
    return await EntryLogSchemaLite.from_tortoise_orm(await add_leave_log((await audit_log.related_to).plate))


@router.put('/order', description='生成订单', response_model=FeeRecordSchema, status_code=201)
async def order(
        fee_record: FeeRecord = Depends(generate_fee_record),
        audit_log: AuditLog = Depends(add_audit_log(ActionType.GENERATE_ORDER)),
):
    if (await (await fee_record.belongs_to).belongs_to).plate != (await audit_log.related_to).plate:
        raise HTTPException(400, dict(
            detail="plate not matched",
        ))
    return await FeeRecordSchema.from_tortoise_orm(fee_record)


class PlateResponse(BaseModel):
    class ResultItem(BaseModel):
        class XYPair(BaseModel):
            x: int
            y: int
        color: int
        license_plate_number: str
        bound: Dict[str, XYPair]
    image_id: str
    request_id: str
    time_used: int
    results: List[ResultItem]


@router.post('/detect_plate', description='识别车牌', response_model=PlateResponse)
async def detect_plate(
        imageb64: str = Body(""),
):
    if imageb64 == "":
        return HTTPException(400, dict(detail="invaild image"))
    form = aiohttp.FormData()
    form.add_field("api_key", settings.API_KEY)
    form.add_field("api_secret", settings.API_SECRET)
    form.add_field("image_base64", imageb64)
    async with aiohttp.request(
            "POST",
            "https://api-cn.faceplusplus.com/imagepp/v1/licenseplate",
            data=form,
    ) as resp:
        res = parse_obj_as(PlateResponse, await resp.json())
        return res

