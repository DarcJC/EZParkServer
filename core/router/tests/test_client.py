import random
import string
from typing import Tuple
from unittest import IsolatedAsyncioTestCase
from uuid import UUID

import requests.auth
from starlette.testclient import TestClient

from core.app import app
from core.models.client import generate_client_token


class EZClientAuth(requests.auth.AuthBase):
    def __init__(self, uuid: UUID, token: str = None):
        self.uuid = uuid
        self.token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.prepare_url(request.url, dict(
            uuid=self.uuid,
            token=self.token,
        ))
        return request


class TestClientEndpointSuccess(IsolatedAsyncioTestCase):

    ut_pair: Tuple[UUID, str]

    async def asyncSetUp(self) -> None:
        with TestClient(app) as _:
            self.__class__.ut_pair = await generate_client_token()

    async def test_001_vehicle_entry(self):
        with TestClient(app) as client:
            uid, token = self.__class__.ut_pair
            resp = client.put('/client/entry', params=dict(
                vehicle_plate=''.join(random.choices(string.ascii_letters, k=8)),
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 201)
