class Component:
    def __init__(self):
        self.entity = None
        self.enabled = True

    def attach(self, entity):
        """Called when the component is attached to an entity"""
        self.entity = entity

    def detach(self):
        """Called when the component is detached from an entity"""
        self.entity = None

    def update(self):
        """Update logic for the component"""
        pass

    def render(self, screen, camera_offset=(0, 0)):
        """Render logic for the component"""
        pass

    def handle_event(self, event):
        """Handle events for the component"""
        pass
