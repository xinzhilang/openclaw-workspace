import asyncio
import websockets

async def handler(ws, path):
    print('Handler called')
    try:
        await ws.send(b'Welcome')
        print('Sent welcome')
        async for msg in ws:
            print('Got:', msg)
            await ws.send(b'Echo')
    except Exception as e:
        print('Handler error:', e)
    finally:
        print('Handler done')

async def main():
    print('Starting server')
    # Try different settings
    async with websockets.serve(
        handler,
        'localhost',  # Try localhost instead of 0.0.0.0
        18795,
        ping_interval=None,  # Disable ping
        compression=None,  # Disable compression
        max_size=None,  # No size limit
        max_queue=None  # No queue limit
    ):
        print('Server running on 18795')
        await asyncio.Future()

asyncio.run(main())
