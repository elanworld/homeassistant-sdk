class Entity:
    id = None
    type = None
    event = None
    state = None
    entity_id = None

    def __init__(self, data=None):
        if data:
            self.__dict__ = data
        if self.event and self.event.__dict__.get("data") and self.event.__dict__.get("data").__dict__.get("entity_id"):
            self.entity_id = self.event.__dict__.get("data").__dict__.get("new_state") and self.event.__dict__.get(
                "data").__dict__.get("entity_id")
        if self.event and self.event.__dict__.get("data") and self.event.__dict__.get("data").__dict__.get(
                "new_state") and self.event.__dict__.get("data").__dict__.get("new_state").__dict__.get("state"):
            self.state = self.event.__dict__.get("data").__dict__.get("new_state") and self.event.__dict__.get(
                "data").__dict__.get("new_state").__dict__.get("state")

    def __str__(self):
        return self.__dict__.__str__()
