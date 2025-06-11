from ..core.component import Component
from .client import Client

def _get_attr(obj, path: str):
    for part in path.split('.'):
        obj = getattr(obj, part)
    return obj

def _set_attr(obj, path: str, value):
    parts = path.split('.')
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], value)

class SyncComponent(Component):
    """Component to synchronize an entity with the DedicatedServer."""

    def __init__(self, client: Client, *, tracked_attrs=None,
                 serialize_fn=None, apply_fn=None):
        super().__init__()
        self.client = client
        self.tracked_attrs = tracked_attrs or ['position.x', 'position.y']
        self.serialize_fn = serialize_fn or self._default_serialize
        self.apply_fn = apply_fn or self._default_apply
        self.client.recv_callback = self._on_message

    def attach(self, entity):
        super().attach(entity)
        self.client.start()

    def detach(self):
        self.client.stop()
        super().detach()

    def tick(self):
        if not self.entity:
            return
        self.client.send_update(self.serialize_fn())

    def _default_serialize(self):
        return {key: _get_attr(self.entity, key) for key in self.tracked_attrs}

    def _default_apply(self, data: dict):
        if not self.entity:
            return
        for key, value in data.items():
            try:
                _set_attr(self.entity, key, value)
            except AttributeError:
                continue

    def _on_message(self, msg: dict):
        if msg.get('player') == self.client.player_id:
            return
        if msg.get('cmd') == 'update':
            self.apply_fn(msg.get('data', {}))
