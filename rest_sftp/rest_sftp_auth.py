import json
import logging
import time

import requests
from requests.auth import HTTPBasicAuth


class Auth:
    def __init__(self):
        pass

    def get_auth(self):
        pass


class BasicAuth(Auth):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.username, self.password)


class OAuth2(Auth):
    def __init__(self, uri: str, realm: str, client_id: str, client_secret: str, username: str = None,
                 password: str = None):
        super().__init__()
        self.uri = uri
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token = None
        self.expires_in = 0

    def _get_payload(self):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        if self.password is not None:
            payload["grant_type"] = "password"
            payload["username"] = self.username
            payload["password"] = self.password
        else:
            payload["grant_type"] = "client_credentials"

        return payload

    def get_auth(self):
        if self.access_token is None or time.time() > self.expires_in:
            logging.info("get a new token")
            r = self._get_auth()
            self.access_token = r["access_token"]
            self.expires_in = int(time.time()) + r["expires_in"]
        return self.access_token

    def _get_auth(self):
        url = f"{self.uri}/auth/realms/{self.realm}/protocol/openid-connect/token"

        payload = self._get_payload()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, headers=headers, data=payload)

        response_json = json.loads(response.text)
        return response_json
