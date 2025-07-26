"""Stream delayed quotes and emit to dashboard via Socket.IO."""

from __future__ import annotations

import json
import logging

import websocket

from .api import API_KEY, WS_URL
from ..webapp import socketio


def stream_overview(symbols: str = "AAPL") -> None:
    """Stream delayed quotes for ``symbols`` and emit via Socket.IO."""

    def on_open(ws):
        auth = json.dumps({"action": "auth", "params": API_KEY})
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

    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    logging.info("Streaming delayed quotes for %s", symbols)
    ws.run_forever()
