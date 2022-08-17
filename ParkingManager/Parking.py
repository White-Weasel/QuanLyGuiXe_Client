import datetime
import requests
from . import BACKEND_URL


class ParkingInfo:
    def __init__(self, plate, ticket=None, time_in=None, time_out=None, face=None):
        self.face = face
        self.time_out = time_out
        self.time_in = time_in
        self.plate = plate
        self.ticket = ticket

        if ticket == '':
            self.ticket = None

        if self.time_in is None:
            self.time_in = datetime.datetime.now()

    def json(self, action: str = None):
        result = {
            'ticket': self.ticket,
            'plate': self.plate,
            'face': self.face,
        }
        if action is not None:
            result['action'] = action
        return result

    def entry(self):
        data = self.json(action='in')
        return requests.post(f"http://{BACKEND_URL}/parking", json=data)

    def out(self):
        data = self.json(action='out')
        return requests.post(f"http://{BACKEND_URL}/parking", json=data)
