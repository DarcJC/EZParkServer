import random
import string
from typing import Tuple
from unittest import IsolatedAsyncioTestCase
from uuid import UUID

import requests.auth
from starlette.testclient import TestClient
from tortoise.exceptions import DoesNotExist

from core.app import app
from core.models import FeeRecordSchema
from core.models.client import generate_client_token
from core.models.vehicle import EntryLogSchemaLite, VehicleType, get_fee_rule


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


class TestClientEndpoint(IsolatedAsyncioTestCase):

    ut_pair: Tuple[UUID, str]
    plate: str

    async def test_000_vehicle_leave_without_enter(self):
        with TestClient(app) as client:
            self.__class__.ut_pair = await generate_client_token()
            self.__class__.plate = ''.join(random.choices(string.ascii_letters, k=8))
            uid, token = self.__class__.ut_pair
            resp = client.delete('/client/entry', params=dict(
                vehicle_plate=self.__class__.plate,
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 404)

    async def test_001_vehicle_entry(self):
        with TestClient(app) as client:
            uid, token = self.__class__.ut_pair
            resp = client.put('/client/entry', params=dict(
                vehicle_plate=self.__class__.plate,
                vehicle_type=-1,
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 201)
            res = EntryLogSchemaLite(**resp.json())
            self.__class__.entry_log_id = res.id

    async def test_002_generate_order_without_end_time(self):
        with TestClient(app) as client:
            uid, token = self.__class__.ut_pair
            resp = client.put('/client/order', params=dict(
                vehicle_plate=self.__class__.plate,
                entry_log_id=self.__class__.entry_log_id,
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 406)

    async def test_003_vehicle_leave(self):
        with TestClient(app) as client:
            uid, token = self.__class__.ut_pair
            resp = client.delete('/client/entry', params=dict(
                vehicle_plate=self.__class__.plate,
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 200)
            res = EntryLogSchemaLite(**resp.json())
            self.__class__.entry_log_id = res.id

    async def test_004_generate_order(self):
        with TestClient(app) as client:
            uid, token = self.__class__.ut_pair
            resp = client.put('/client/order', params=dict(
                vehicle_plate=self.__class__.plate,
                entry_log_id=self.__class__.entry_log_id,
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 201)
            FeeRecordSchema(**resp.json())

    async def test_005_bad_plate(self):
        with TestClient(app) as client:
            uid, token = self.__class__.ut_pair
            resp = client.put('/client/order', params=dict(
                vehicle_plate=''.join(random.choices(string.digits, k=8)),
                entry_log_id=self.__class__.entry_log_id,
            ), auth=EZClientAuth(uid, token))
            self.assertEqual(resp.status_code, 400)

    async def test_006_fee_rule_not_set(self):
        with TestClient(app) as _:
            with self.assertRaises(DoesNotExist) as context:
                await get_fee_rule(VehicleType.UNKNOWN)
