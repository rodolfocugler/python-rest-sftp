import json
import logging

import requests
from requests_toolbelt import MultipartEncoder

from rest_sftp.rest_sftp_auth import OAuth2


def _get_headers(auth, headers=None):
    if headers is None:
        return {"Authorization": f"Bearer {auth.get_auth()}"}
    else:
        headers["Authorization"] = f"Bearer {auth.get_auth()}"
        return headers


def _download_file(r, local_path):
    r.raise_for_status()
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


class RestSFTP:
    def __init__(self, uri, auth):
        self.uri = uri
        self.auth = auth

    def read_tree(self, folder="/", recursive_enabled=False, ignore_hidden_file_enabled=True,
                  absolute_path_enabled=False):
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
        logging.debug(f"read_tree: {params} - {r.status_code}")
        return json.loads(r.text)

    def upload_file_url(self, url, filepath, filename):
        rest_sftp_url = f"{self.uri}/api/commands/url"

        if isinstance(self.auth, OAuth2):
            r = requests.post(rest_sftp_url, headers=_get_headers(self.auth),
                              data={"url": url, "filepath": filepath, "filename": filename})
        else:
            r = requests.post(rest_sftp_url, auth=self.auth.get_auth(),
                              data={"url": url, "filepath": filepath, "filename": filename})
        logging.debug(f"upload_file_url: {url, filepath, filename} - {r.status_code}")

    def download_file(self, file_paths, local_path, zip_enabled):
        url = f"{self.uri}/api/commands"

        if isinstance(self.auth, OAuth2):
            with requests.get(url, headers=_get_headers(self.auth),
                              params={"file_paths": file_paths, "zip_enabled": zip_enabled}) as r:
                logging.debug(f"download_file: {file_paths, local_path, zip_enabled} - {r.status_code}")
                _download_file(r, local_path)
        else:
            with requests.get(url, auth=self.auth.get_auth(),
                              params={"file_paths": file_paths, "zip_enabled": zip_enabled}) as r:
                logging.debug(f"download_file: {file_paths, local_path, zip_enabled} - {r.status_code}")
                _download_file(r, local_path)

    def upload_file(self, dst_folder_path, filename, local_path):
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
        logging.debug(f"upload_file: {dst_folder_path, filename, local_path} - {r.status_code}")

    def delete_file(self, filepath, move_to_bin_enabled):
        params = {"filepath": filepath, "move_to_bin_enabled": move_to_bin_enabled}
        url = f"{self.uri}/api/commands"
        logging.debug(f"delete_file: {filepath, move_to_bin_enabled}")
        if isinstance(self.auth, OAuth2):
            r = requests.delete(url, headers=_get_headers(self.auth), params=params)
        else:
            r = requests.delete(url, auth=self.auth.get_auth(), params=params)
        logging.debug(f"delete_file: {filepath, move_to_bin_enabled} - {r.status_code}")

    def move_file(self, filepath_from, filepath_to):
        data = {"filepath_from": filepath_from, "filepath_to": filepath_to}
        url = f"{self.uri}/api/commands"

        logging.debug(f"move_file: {filepath_from, filepath_to}")
        if isinstance(self.auth, OAuth2):
            r = requests.put(url, data=data, headers=_get_headers(self.auth))
        else:
            r = requests.put(url, auth=self.auth.get_auth(), data=data)
        logging.debug(f"move_file: {filepath_from, filepath_to} - {r.status_code}")
