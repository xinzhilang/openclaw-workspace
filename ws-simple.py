import asyncio
import websockets
import json

async def handler(ws, path):
    addr = ws.remote_address
    print(f'Client: {addr}')
    await ws.send(json.dumps({'type': 'welcome', 'status': 'ok'}))
    try:
        async for msg in ws:
            print(f'Got: {msg[:50]}')
            await ws.send(json.dumps({'type': 'ack'}))
    except Exception as e:
        print(f'Error: {e}')

async def main():
    print('Starting WS on 18793')
    async with websockets.serve(handler, '0.0.0.0', 18793):
        await asyncio.Future()

asyncio.run(main())
