import unittest

import requests.auth
from starlette.testclient import TestClient

from core import settings
from core.app import app
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
            resp = client.delete("/manage/client_token", auth=EZAdminAuth(self.token),
                                 json=dict(uuid=self.__class__.uuid.__str__()))
            self.assertEqual(resp.status_code, 204)
