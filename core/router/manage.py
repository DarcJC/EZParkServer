from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, constr

from core.dependencies import require_admin_token
from core.models.client import generate_client_token

router = APIRouter(prefix="/manage", tags=["管理"])


class NewClientTokenResponse(BaseModel):
    uuid: UUID
    token: constr(min_length=128)


@router.put("/client", description="创建一个客户端凭据", response_model=NewClientTokenResponse, status_code=201)
async def client_token(
    _: bool = Depends(require_admin_token),
):
    uuid, token = await generate_client_token()
    return NewClientTokenResponse(uuid=uuid, token=token)

