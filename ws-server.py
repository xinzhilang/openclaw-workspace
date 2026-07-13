
import asyncio, websockets, json

async def handler(ws, path):
    await ws.send(json.dumps({"type": "welcome", "status": "ok"}))
    try:
        async for msg in ws:
            print(f"Received: {msg[:50]}")
            try:
                data = json.loads(msg)
                if data.get("type") == "ping":
                    await ws.send(json.dumps({"type": "pong"}))
                else:
                    await ws.send(json.dumps({"type": "ack"}))
            except:
                await ws.send(json.dumps({"type": "error"}))
    except:
        pass

async def main():
    async with websockets.serve(handler, "0.0.0.0", 18793, ping_interval=20):
        print("WebSocket server on port 18793")
        await asyncio.Future()

asyncio.run(main())
