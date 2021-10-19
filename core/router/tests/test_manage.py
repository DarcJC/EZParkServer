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
            resp = client.put("/manage/client", auth=EZAdminAuth(self.token))
            _ = NewClientTokenResponse(**resp.json())
            self.assertEqual(resp.status_code, 201)
