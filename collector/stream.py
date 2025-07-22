import json
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
        print(message)
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
                    print("Real-time feed unauthorized, switching to delayed feed...")
                    ws.close()
                    stream_quotes(symbols, realtime=False)
                else:
                    print("Subscription unauthorized; check your plan permissions")

    def on_error(ws, error):
        print("WebSocket error:", error)

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed", close_status_code, close_msg)

    url = REALTIME_WS_URL if realtime else WS_URL
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    print(
        f"Streaming {'real-time' if realtime else 'delayed'} data for {symbols}... press Ctrl+C to stop"
    )
    ws.run_forever()
