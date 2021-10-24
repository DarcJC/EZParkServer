import random
import unittest

import requests.auth
from starlette.testclient import TestClient

from core import settings
from core.app import app
from core.models.vehicle import VehicleType, FeeRuleSchemaLite
from core.router.manage import NewClientTokenResponse


class EZAdminAuth(requests.auth.AuthBase):
    def __init__(self, token: str = None):
        self.token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.prepare_url(request.url, dict(
            token=self.token,
        ))
        return request


class TestManageEndpointSuccess(unittest.TestCase):
    token = settings.ADMIN_TOKEN

    def test_001_generate_client_token(self):
        with TestClient(app) as client:
            resp = client.put("/manage/client_token", auth=EZAdminAuth(self.token))
            res = NewClientTokenResponse(**resp.json())
            self.__class__.uuid = res.uuid
            self.assertEqual(resp.status_code, 201)

    def test_002_deactivate_client_token(self):
        with TestClient(app) as client:
            resp = client.delete(f"/manage/client_token/{self.__class__.uuid}", auth=EZAdminAuth(self.token),)
            self.assertEqual(resp.status_code, 204)

    def test_003_create_new_fee_rule(self):
        with TestClient(app) as client:
            resp = client.put("/manage/fee_rule", auth=EZAdminAuth(self.token),
                              json=dict(
                                  vehicle_type=VehicleType.TESTING,
                                  unit_fee=random.randint(0, 256),
                                  priority=random.randint(-16, 15)
                              ))
            self.assertEqual(resp.status_code, 201)
            res = FeeRuleSchemaLite(**resp.json())
            self.__class__.fee_rule_id = res.id
            
    def test_004_deactivate_fee_rule(self):
        with TestClient(app) as client:
            resp = client.delete(f'/manage/fee_rule/{self.__class__.fee_rule_id}', auth=EZAdminAuth(self.token))
            self.assertEqual(resp.status_code, 204)
