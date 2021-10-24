from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, constr, conint, condecimal

from core.dependencies import require_admin_token
from core.models.client import generate_client_token, deactivate_client_token
from core.models.vehicle import VehicleType, add_fee_rule, FeeRuleSchemaLite

router = APIRouter(prefix="/manage", tags=["管理"])


class NewClientTokenResponse(BaseModel):
    uuid: UUID
    token: constr(min_length=128)


@router.put("/client_token", description="创建一个客户端凭据", response_model=NewClientTokenResponse, status_code=201)
async def client_token(
    _: bool = Depends(require_admin_token),
):
    uuid, token = await generate_client_token()
    return NewClientTokenResponse(uuid=uuid, token=token)


@router.delete("/client_token/{ct_id}", description="将客户端凭据标记为无效", status_code=204)
async def client_token(
    ct_id: UUID,
    _: bool = Depends(require_admin_token),
):
    await deactivate_client_token(ct_id)
    return None


class AddFeeRuleModel(BaseModel):
    vehicle_type: VehicleType
    unit_fee: condecimal(ge=Decimal(value='1'))
    priority: Optional[conint(ge=-16, le=15)] = 0


@router.put("/fee_rule", description='添加收费规则', status_code=201, response_model=FeeRuleSchemaLite)
async def fee_rule(
        payload: AddFeeRuleModel,
        _: bool = Depends(require_admin_token),
):
    return await FeeRuleSchemaLite.from_tortoise_orm(await add_fee_rule(**payload.dict(exclude_unset=True)))


@router.delete("/fee_rule/{fid}", description='将收费规则标记为无效', status_code=204)
async def fee_rule(
    fid: int,
):
    pass
