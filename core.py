import json
import threading
import time

import websocket
from . import event
from websocket import WebSocketApp


class HomeAssistantSdk:
    def __init__(self, url, token):
        self.current_id = 101
        self.token = token
        self.authed = False
        self.fun_message = None
        self.debug = False
        self.app = websocket.WebSocketApp(f'ws://{url}/api/websocket', on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close, on_open=self.on_open)
        threading.Thread(target=self.app.run_forever).start()
        while not self.authed:
            time.sleep(0.1)

    def on_message(self, ws, message):
        if self.debug:
            print(message)
        if not self.authed or self.fun_message:
            loads = json.loads(message)  # type: dict
            if self.fun_message:
                self.fun_message(json.loads(message, object_hook=event.Event))
            if not self.authed and loads.get("type") == "auth_ok":
                self.authed = True

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws: WebSocketApp):
        ws.send(
            '{"type": "auth", "access_token": "%s"}' % self.token)

    def listen_message(self, fun):
        """
        deal with the message from server
        :param fun: function(Event)
        :return:
        """
        self.fun_message = fun

    def subscribe_events(self, ):
        data = {"id": ++ self.current_id, "type": "subscribe_events", "event_type": "state_changed"}
        self.app.send(json.dumps(data))

    def send(self, message: dict):
        message["id"] = ++ self.current_id

