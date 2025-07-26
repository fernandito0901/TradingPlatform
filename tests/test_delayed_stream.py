import json
import os

os.environ.setdefault("POLYGON_API_KEY", "x")
os.environ.setdefault("NEWS_API_KEY", "x")

from trading_platform.collector import delayed_stream


class DummySocket:
    def __init__(self):
        self.emitted = []

    def emit(self, event, data):
        self.emitted.append((event, data))


def test_stream_overview(monkeypatch):
    sock = DummySocket()
    monkeypatch.setattr(delayed_stream, "socketio", sock)

    def ws_app(url, on_open=None, on_message=None, on_error=None, on_close=None):
        class WS:
            def send(self_inner, *_):
                pass

            def run_forever(self_inner):
                if on_open:
                    on_open(self_inner)
                msg = json.dumps(
                    [{"status": "auth_success"}, {"ev": "Q", "sym": "AAPL", "p": 100}]
                )
                if on_message:
                    on_message(self_inner, msg)

        return WS()

    monkeypatch.setattr(delayed_stream.websocket, "WebSocketApp", ws_app)
    delayed_stream.stream_overview("AAPL")
    assert ("overview_quote", {"symbol": "AAPL", "p": 100}) in sock.emitted
