import hashlib
import random
import string
import uuid
from typing import Union, Tuple

from pydantic import constr
from tortoise import Model, fields


class ClientToken(Model):
    uuid = fields.UUIDField(pk=True)
    token = fields.CharField(max_length=256, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    access_at = fields.DatetimeField(default=None, null=True)
    valid = fields.BooleanField(default=True)

    @staticmethod
    def encrypt_token(pure_token: str) -> constr(max_length=256):
        return hashlib.sha256(pure_token.encode('utf-8')).hexdigest()


async def authenticate(_uuid: uuid.UUID, token: str) -> ClientToken:
    """
    验证客户端凭据
    如果正确会返回一个`ClientToken` 否则返回`None`
    :param _uuid: 客户端UUID
    :param token: 客户端凭据
    :return:
    """
    encrypted_token = ClientToken.encrypt_token(token)
    return await ClientToken.get(uuid=_uuid, token=encrypted_token)


async def generate_client_token() -> Tuple[uuid.UUID, str]:
    pure_token = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    obj = await ClientToken.create(token=ClientToken.encrypt_token(pure_token))
    return obj.uuid, pure_token
