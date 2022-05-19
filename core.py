import json
import threading
import time
from typing import Optional, List, Dict, Union

import requests
import websocket
from .entity import Entity
from websocket import WebSocketApp


class HomeAssistantSdk:
    str_last_info = "_last_info"

    def __init__(self, url, token):
        self.current_id = 100
        self._url = url
        self._token = token
        self._api = f"http://{self._url}/api"
        self.authed = False
        self.debug = False
        self.reconnect_duration = None
        self.id_fun_map = {}
        self.app = websocket.WebSocketApp(f'ws://{url}/api/websocket', on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close, on_open=self.on_open)
        threading.Thread(target=self.app.run_forever).start()
        for _ in range(100):
            if self.authed:
                break
            time.sleep(0.1)

    def on_message(self, ws, message):
        if self.debug:
            print(message)
        if not self.authed or self.id_fun_map:
            loads = json.loads(message)  # type: dict
            if loads.get("id") in self.id_fun_map:
                id_fun = self.id_fun_map[loads.get("id")]
                if id_fun:
                    id_fun(json.loads(message, object_hook=Entity))
                self.id_fun_map[f"{loads.get('id')}{self.str_last_info}"] = json.loads(message)
            if not self.authed and loads.get("type") == "auth_ok":
                self.authed = True
                print(f"{self} authed")

    def on_error(self, ws, error):
        print(f"error: {error}")

    def on_close(self, ws, *args):
        self.authed = False
        print(f"closed: {args}")
        self.reconnect()

    def on_open(self, ws: WebSocketApp):
        ws.send(
            '{"type": "auth", "access_token": "%s"}' % self._token)

    def reconnect(self):
        if self.reconnect_duration:
            time.sleep(self.reconnect_duration)
            self.__init__(self._url, self._token)

    def subscribe_events(self, fun):
        data = {"type": "subscribe_events", "event_type": "state_changed"}
        self.app.send(json.dumps(self._id_cal(data)))
        self.id_fun_map[self.current_id] = fun
        return self.current_id

    def send(self, payload: dict, fun=None):
        self.app.send(json.dumps(self._id_cal(payload)))
        self.id_fun_map[self.current_id] = fun
        return self.current_id

    def _id_cal(self, message: dict):
        self.current_id += 1
        message["id"] = + self.current_id
        return message

    def get_state(self, entity_id=None):
        states_ = {"type": "get_states"}
        id_ = self.send(self._id_cal(states_))
        while True:
            last_info = self.id_fun_map.get(f"{id_}{self.str_last_info}")
            if last_info is not None:
                entities = last_info.get("result")
                if entity_id:
                    for entity in entities:
                        if entity.get("entity_id") == entity_id:
                            return json.loads(json.dumps(entity), object_hook=Entity)
                    return None
                else:
                    return entities
            time.sleep(0.1)

    def subscribe_trigger(self, entity_id, fun):
        data = {
            "type": "subscribe_trigger",
            "trigger": {
                "platform": "state",
                "entity_id": entity_id
            },
        }
        self.send(data, fun)

    def get_object_attr(self, object, attrs: list):
        current = object
        for attr in attrs:
            current = current.__dict__.get(attr)
            if current is None:
                return None
        return current

    def request(
            self,
            path,
            method="GET",
            data=None,
            **kwargs,
    ) -> Union[dict, list, str]:
        resp = requests.request(
            method,
            path,
            json=data,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            **kwargs,
        )
        if resp.status_code != 200:
            raise IOError(
                f'Home Assistant respond error:{resp.text}'
            )
        return resp.json()

    def set_state(self, entity, state, **payload):
        attributes = "attributes"
        api_ = f"{self._api}/states/{entity}"
        state_ = self.request(api_)
        attr = state_.get(attributes)
        payload[attributes] = attr
        payload["state"] = state
        return self.request(api_, method="POST", data=payload)
