import json
import logging
import websocket

from .api import API_KEY, REALTIME_WS_URL, WS_URL


def stream_quotes(symbols="AAPL", realtime=False):
    """Stream trades and quotes via Polygon's WebSocket."""

    def on_open(ws):
        auth = json.dumps({"action": "auth", "params": API_KEY})
        ws.send(auth)

    def subscribe(ws):
        chans = []
        for sym in symbols.split(","):
            chans.append(f"T.{sym}")
            chans.append(f"Q.{sym}")
        subs = json.dumps({"action": "subscribe", "params": ",".join(chans)})
        ws.send(subs)

    def on_message(ws, message):
        logging.debug(message)
        try:
            events = json.loads(message)
        except json.JSONDecodeError:
            return
        for evt in events:
            if evt.get("status") == "auth_success":
                subscribe(ws)
            elif (
                evt.get("status") == "error" and evt.get("message") == "not authorized"
            ):
                if realtime:
                    logging.warning(
                        "Real-time feed unauthorized, switching to delayed feed..."
                    )
                    ws.close()
                    stream_quotes(symbols, realtime=False)
                else:
                    logging.error(
                        "Subscription unauthorized; check your plan permissions"
                    )

    def on_error(ws, error):
        logging.error("WebSocket error: %s", error)

    def on_close(ws, close_status_code, close_msg):
        logging.info("WebSocket closed %s %s", close_status_code, close_msg)

    url = REALTIME_WS_URL if realtime else WS_URL
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    logging.info(
        "Streaming %s data for %s... press Ctrl+C to stop",
        "real-time" if realtime else "delayed",
        symbols,
    )
    ws.run_forever()
