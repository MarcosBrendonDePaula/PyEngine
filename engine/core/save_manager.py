import json
import os

class SaveManager:
    def __init__(self, path: str = 'savegame.json'):
        self.path = path

    def save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {}
