import time
from datetime import datetime

import requests
import json
from app.settings import taxcom_settings
from abc import ABC


class Taxcom(ABC):
    url: str = "https://api-lk-ofd.taxcom.ru/API/v2/"
    data_auth: dict = {
        "login": taxcom_settings.LOGIN,
        "password": taxcom_settings.PASSWORD,
    }
    output_data = {}
    token = None
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Taxcom, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        self.session = requests.session()
        self._refresh()

    def _build_url(self, name):
        return f"{self.url}{name}"

    def _get(self, name, params=None):
        attemps = 3
        url = self._build_url(name)
        for _ in range(attemps):
            response = self.session.get(url, headers=self.headers, params=params)
            if response.ok:
                return response.json()
            elif response.status_code == 401:
                self._refresh(True)
                attemps -= 1
            else:
                print(f"Error ({response.status_code})")
                break
            time.sleep(1)
        raise Exception(f"Error get from {url} at {datetime.now()}")

    def _refresh(self, force=False):
        if force or not self.token:
            print(f"Refreshed in {datetime.now()} at {self.__class__}")
            auth_response = self.session.post(
                self._build_url("Login"),
                data=json.dumps(self.data_auth),
                headers={
                    "Content-type": "application/json",
                    "Content-Encoding": "utf-8",
                    "Integrator-ID": taxcom_settings.INTEGRATOR_ID,
                },
            ).json()
            self.token = auth_response.get("sessionToken")
            self.headers = {"Session-Token": self.token}
