"""Asynchronous WebSocket streaming utilities."""

from __future__ import annotations

import json
import logging

import websockets

from .api_async import API_KEY, WS_URL, REALTIME_WS_URL


async def stream_quotes(symbols: str = "AAPL", realtime: bool = False) -> None:
    """Stream trades and quotes via Polygon's WebSocket asynchronously.

    Parameters
    ----------
    symbols : str, default "AAPL"
        Comma-separated ticker symbols to subscribe to.
    realtime : bool, default False
        If ``True`` use the real-time feed, otherwise the delayed feed.
    """

    url = REALTIME_WS_URL if realtime else WS_URL
    async with websockets.connect(url) as ws:
        auth = json.dumps({"action": "auth", "params": API_KEY})
        await ws.send(auth)
        chans = []
        for sym in symbols.split(","):
            chans.append(f"T.{sym}")
            chans.append(f"Q.{sym}")
        subs = json.dumps({"action": "subscribe", "params": ",".join(chans)})
        await ws.send(subs)
        logging.info(
            "Streaming %s data for %s... press Ctrl+C to stop",
            "real-time" if realtime else "delayed",
            symbols,
        )
        async for message in ws:
            logging.debug(message)
            try:
                events = json.loads(message)
            except json.JSONDecodeError:
                continue
            for evt in events:
                if (
                    evt.get("status") == "error"
                    and evt.get("message") == "not authorized"
                ):
                    if realtime:
                        logging.warning(
                            "Real-time feed unauthorized, switching to delayed feed..."
                        )
                        await ws.close()
                        await stream_quotes(symbols, realtime=False)
                        return
                    logging.error(
                        "Subscription unauthorized; check your plan permissions"
                    )
                    return
