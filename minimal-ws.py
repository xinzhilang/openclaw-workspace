import asyncio
import websockets

async def handler(ws, path):
    print('Client connected')
    await ws.send(b'Hello')
    try:
        async for msg in ws:
            print('Received:', msg[:20])
            await ws.send(b'Echo: ' + msg)
    except Exception as e:
        print('Error:', e)

async def main():
    print('Starting...')
    async with websockets.serve(handler, '0.0.0.0', 18794):
        await asyncio.Future()

asyncio.run(main())
