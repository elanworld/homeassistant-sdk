a python lib to connect homeassistant using websocket

usage:

```python
from homeassistant_sdk import HomeassistantSdk
from entity import Entity

def function(entity: Entity):
    print(entity)

sdk = HomeassistantSdk( "localhost:8123", "auth token")
sdk.subscribe_trigger("switch.entity_id", fun=function)
```