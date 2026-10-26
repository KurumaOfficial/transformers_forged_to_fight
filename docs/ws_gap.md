# WebSocket /ws gap (Step 8.2)

## Client behavior

`[RUN]` The client logs every ~1 s:

```
[NetWebSocket] WebSocketError: Invalid handshake response: HTTP/1.1 400 Bad Request
  at EB.Net.WebSocket+Impl.SendUpgradeRequest ...
```

The request is a standard upgrade (`Upgrade: websocket`,
`Connection: Upgrade`, `Sec-WebSocket-Key`, `Sec-WebSocket-Version: 13`).
The stub's `do_GET` explicitly returns 400 for `/ws` and any upgrade request
(`server/stub_server.py`, lines around 138).

## What a minimal response needs

A correct upgrade is not just a 101 header: the server must compute
`Sec-WebSocket-Accept = base64(SHA1(key + GUID))` and then speak RFC6455
frames. A fake 101 without a frame loop would leave the client connected and
waiting, which **changes behavior** and may hide the real timeout. The user
asked for a minimal response only if it does not change behavior; a fake 101
does change it.

## Decision

Keep the 400 for now. The retry is noisy but does not crash the client or block
the HTTP flow. The real fix is a small WebSocket server with the Sparx
subscribe/handshake messages; that needs the first client message capture,
which is not available because the handshake never completes.

## Next (blocked)

1. Capture the client's first WebSocket frame after a valid 101 (requires a
   real WS endpoint, not a fake header).
2. Implement the Sparx component/message subscription format.
3. Verify no duplicate HTTP fallback and no behavior change.

Until then, `/ws` remains a documented 400, not a silent fake success.
