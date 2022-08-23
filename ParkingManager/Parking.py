import datetime
import requests
from . import BACKEND_URL


class ParkingInfo:
    def __init__(self, plate: str = None,
                 ticket: int = None,
                 time_in: datetime.datetime = None,
                 time_out: datetime.datetime = None,
                 inside: bool = None,
                 face: str = None):
        if ticket == '':
            self.ticket = None

        self._data = {
            'plate': plate,
            'ticket': ticket,
            'time_in': time_in,
            'time_out': time_out,
            'inside': inside,
            'face': face,
        }

    def __getattr__(self, item):
        return self._data[item]

    def json(self, action: str = None, accept_none: bool = False):
        result = self._data
        if not accept_none:
            result = {key: value for key, value in result.items() if value is not None}
        if action is not None:
            result['action'] = action
        return result

    def entry(self):
        data = self.json(action='in')
        return requests.post(f"http://{BACKEND_URL}/parking", json=data)

    def out(self):
        data = self.json(action='out')
        return requests.post(f"http://{BACKEND_URL}/parking", json=data)

    def search(self):
        data = self.json()
        return requests.get(f"http://{BACKEND_URL}/parking_search", params=data)
