#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('Relay')

PORT = 18792

async def handler(websocket, path):
    addr = websocket.remote_address
    logger.info(f'[{datetime.now().strftime("%H:%M:%S")}] Client: {addr}')
    
    # Send welcome
    await websocket.send(json.dumps({
        'type': 'connected',
        'message': 'OpenClaw Relay Ready'
    }))
    
    try:
        async for message in websocket:
            logger.info(f'Received: {message[:50]}')
            # Echo back
            response = json.dumps({'echo': message, 'ok': True})
            await websocket.send(response)
    except Exception as e:
        logger.error(f'Error: {e}')
    finally:
        logger.info('Disconnected')

async def main():
    logger.info(f'Starting WebSocket server on port {PORT}')
    async with websockets.serve(handler, '0.0.0.0', PORT):
        logger.info(f'Running: ws://localhost:{PORT}')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
