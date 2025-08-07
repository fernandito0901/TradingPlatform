"""Stream delayed quotes and emit to dashboard via Socket.IO."""

from __future__ import annotations

import json
import logging
import time

import websocket

from ..webapp import socketio
from .api import WS_URL, _get_polygon_key


def stream_overview(symbols: str = "AAPL", testing: bool = False) -> None:
    """Stream delayed quotes for ``symbols`` and emit via Socket.IO.

    Parameters
    ----------
    symbols : str, optional
        Symbols to subscribe to, by default "AAPL".
    testing : bool, optional
        If ``True``, stop after the first connection attempt.
    """

    def on_open(ws):
        auth = json.dumps({"action": "auth", "params": _get_polygon_key()})
        ws.send(auth)

    def subscribe(ws):
        chans = [f"Q.{s}" for s in symbols.split(",")]
        subs = json.dumps({"action": "subscribe", "params": ",".join(chans)})
        ws.send(subs)

    def on_message(ws, message):
        try:
            events = json.loads(message)
        except json.JSONDecodeError:
            return
        for evt in events:
            if evt.get("status") == "auth_success":
                subscribe(ws)
            elif evt.get("ev") == "Q":
                quote = {
                    "symbol": evt.get("sym") or evt.get("symbol"),
                    "p": evt.get("p") or evt.get("ap"),
                }
                socketio.emit("overview_quote", quote)

    def on_error(ws, error):
        logging.error("WebSocket error: %s", error)

    def on_close(ws, code, msg):
        logging.info("WebSocket closed %s %s", code, msg)

    backoff = 1
    while True:
        ws = websocket.WebSocketApp(
            WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        logging.info("Streaming delayed quotes for %s", symbols)
        try:
            ws.run_forever()
        except Exception as exc:  # pragma: no cover - network errors
            logging.error("stream error: %s", exc)
        time.sleep(backoff)
        backoff = min(backoff * 2, 60)
        if testing:
            break
