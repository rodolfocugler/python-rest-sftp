import json
import logging

import requests
from requests import Response
from requests_toolbelt import MultipartEncoder
from rest_sftp.rest_sftp_auth import OAuth2, Auth


def _get_headers(auth: Auth, headers: object = None) -> object:
    if headers is None:
        return {"Authorization": f"Bearer {auth.get_auth()}"}
    else:
        headers["Authorization"] = f"Bearer {auth.get_auth()}"
        return headers


def _download_file(r: Response, local_path: str, chunked: bool):
    r.raise_for_status()
    with open(local_path, "wb") as f:
        if chunked:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        else:
            f.write(r.content)


def _check_response(r: Response, method_name: str, params):
    content = r.text if len(r.content) < 1024 else None
    if r.status_code >= 400:
        logging.error(f"{method_name}: {params} - {r.status_code} - {content}")
        raise Exception(content)
    else:
        logging.debug(f"{method_name}: {params} - {r.status_code} - {content}")


class RestSFTP:
    def __init__(self, uri: str, auth: Auth):
        self.uri = uri
        self.auth = auth

    def read_tree(self, folder: str = "/", recursive_enabled: bool = False, ignore_hidden_file_enabled: bool = True,
                  absolute_path_enabled: bool = False) -> object:
        url = f"{self.uri}/api/tree"
        params = {
            "folder": folder,
            "recursive_enabled": recursive_enabled,
            "ignore_hidden_file_enabled": ignore_hidden_file_enabled,
            "absolute_path_enabled": absolute_path_enabled
        }

        logging.debug(f"read_tree: {params}")
        if isinstance(self.auth, OAuth2):
            r = requests.get(url, headers=_get_headers(self.auth), params=params)
        else:
            r = requests.get(url, auth=self.auth.get_auth(), params=params)
        _check_response(r, "read_tree", (folder, recursive_enabled, ignore_hidden_file_enabled, absolute_path_enabled))
        return json.loads(r.text)

    def upload_file_url(self, url: str, filepath: str, filename: str):
        rest_sftp_url = f"{self.uri}/api/commands/url"

        if isinstance(self.auth, OAuth2):
            r = requests.post(rest_sftp_url, headers=_get_headers(self.auth),
                              data={"url": url, "filepath": filepath, "filename": filename})
        else:
            r = requests.post(rest_sftp_url, auth=self.auth.get_auth(),
                              data={"url": url, "filepath": filepath, "filename": filename})
        _check_response(r, "upload_file_url", (url, filepath, filename))

    def download_content(self, file_path: str, dtype=None):
        url = f"{self.uri}/api/commands"

        if isinstance(self.auth, OAuth2):
            r = requests.get(url, headers=_get_headers(self.auth),
                             params={"file_paths": file_path, "zip_enabled": False})
        else:
            r = requests.get(url, auth=self.auth.get_auth(),
                             params={"file_paths": file_path, "zip_enabled": False})
        _check_response(r, "download_file", file_path)

        if dtype == str:
            return r.text
        return r.content

    def download_file(self, file_paths: str, local_path: str, zip_enabled: bool, chunked: bool = True):
        url = f"{self.uri}/api/commands"

        if isinstance(self.auth, OAuth2):
            with requests.get(url, headers=_get_headers(self.auth),
                              params={"file_paths": file_paths, "zip_enabled": zip_enabled}) as r:
                _download_file(r, local_path, chunked)
                _check_response(r, "download_file", (file_paths, local_path, zip_enabled))
        else:
            with requests.get(url, auth=self.auth.get_auth(),
                              params={"file_paths": file_paths, "zip_enabled": zip_enabled}) as r:
                _download_file(r, local_path, chunked)
                _check_response(r, "download_file", (file_paths, local_path, zip_enabled))

    def upload_file(self, dst_folder_path: str, filename: str, local_path: str):
        data = MultipartEncoder(
            fields={"filepath": dst_folder_path, "f": (filename, open(local_path, "rb"), "text/plain")})
        url = f"{self.uri}/api/commands"

        logging.debug(f"upload_file: {dst_folder_path, filename, local_path}")
        if isinstance(self.auth, OAuth2):
            r = requests.post(url, data=data,
                              headers=_get_headers(self.auth, {"Content-Type": data.content_type}))
        else:
            r = requests.post(url, auth=self.auth.get_auth(), data=data,
                              headers={"Content-Type": data.content_type})
        _check_response(r, "upload_file", (dst_folder_path, filename, local_path))

    def delete_file(self, filepath: str, move_to_bin_enabled: bool):
        params = {"filepath": filepath, "move_to_bin_enabled": move_to_bin_enabled}
        url = f"{self.uri}/api/commands"
        logging.debug(f"delete_file: {filepath, move_to_bin_enabled}")
        if isinstance(self.auth, OAuth2):
            r = requests.delete(url, headers=_get_headers(self.auth), params=params)
        else:
            r = requests.delete(url, auth=self.auth.get_auth(), params=params)
        _check_response(r, "delete_file", (filepath, move_to_bin_enabled))

    def move_file(self, filepath_from: str, filepath_to: str):
        data = {"filepath_from": filepath_from, "filepath_to": filepath_to}
        url = f"{self.uri}/api/commands"

        logging.debug(f"move_file: {filepath_from, filepath_to}")
        if isinstance(self.auth, OAuth2):
            r = requests.put(url, data=data, headers=_get_headers(self.auth))
        else:
            r = requests.put(url, auth=self.auth.get_auth(), data=data)
        _check_response(r, "move_file", (filepath_from, filepath_to))
