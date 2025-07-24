import json
import importlib
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

os.environ.setdefault("POLYGON_API_KEY", "test")

from trading_platform.collector import stream


def test_stream_quotes_reconnect(monkeypatch):
    importlib.reload(stream)

    urls = []

    class FakeWS:
        def __init__(
            self,
            url,
            on_open=None,
            on_message=None,
            on_error=None,
            on_close=None,
        ):
            self.url = url
            self.on_open = on_open
            self.on_message = on_message
            self.on_error = on_error
            self.on_close = on_close

        def send(self, msg):
            pass

        def close(self):
            pass

        def run_forever(self):
            urls.append(self.url)
            if self.on_open:
                self.on_open(self)
            if self.on_message:
                if self.url == stream.REALTIME_WS_URL:
                    msg = json.dumps([{"status": "error", "message": "not authorized"}])
                    self.on_message(self, msg)
                else:
                    msg = json.dumps([{"status": "auth_success"}])
                    self.on_message(self, msg)
            if self.on_close:
                self.on_close(self, None, None)

    monkeypatch.setattr(stream.websocket, "WebSocketApp", FakeWS)

    stream.stream_quotes("AAPL", realtime=True)

    assert urls == [stream.REALTIME_WS_URL, stream.WS_URL]
