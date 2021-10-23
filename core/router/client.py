from fastapi import APIRouter, Depends

from core.dependencies import get_current_client
from core.models import ClientToken

router = APIRouter(prefix='/client', tags=['门岗客户端'])


@router.put('/entry', description='载具进场')
def entry(
        _: ClientToken = Depends(get_current_client),
):
    pass
