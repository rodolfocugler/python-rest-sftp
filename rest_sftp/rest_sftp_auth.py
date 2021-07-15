import json

import requests
from requests.auth import HTTPBasicAuth


class BasicAuth:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_auth(self):
        return HTTPBasicAuth(self.username, self.password)


class OAuth2:
    def __init__(self, uri, realm, client_id, client_secret, username=None, password=None):
        self.uri = uri
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

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
        url = f"{self.uri}/auth/realms/{self.realm}/protocol/openid-connect/token"

        payload = self._get_payload()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, headers=headers, data=payload)

        response_json = json.loads(response.text)
        return response_json["access_token"]
