#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WS')

PORT = 18793

async def handler(ws, path):
    addr = ws.remote_address
    logger.info(f'Client: {addr}')
    
    # Send welcome immediately after connection
    try:
        await ws.send(json.dumps({
            'type': 'welcome',
            'message': 'Connected to Relay',
            'status': 'ok'
        }))
        logger.info('Welcome sent')
    except Exception as e:
        logger.error(f'Could not send welcome: {e}')
        return
    
    # Handle messages
    try:
        async for message in ws:
            logger.info(f'Got message: {message[:50]}')
            try:
                data = json.loads(message)
                # Respond to pings
                if data.get('type') == 'ping':
                    await ws.send(json.dumps({'type': 'pong'}))
                else:
                    await ws.send(json.dumps({'type': 'ack', 'received': True}))
            except:
                await ws.send(json.dumps({'type': 'error'}))
    except websockets.exceptions.ConnectionClosed:
        logger.info('Connection closed normally')
    except Exception as e:
        logger.error(f'Connection error: {e}')

async def main():
    logger.info(f'Starting WebSocket on port {PORT}')
    async with websockets.serve(handler, '0.0.0.0', PORT, ping_interval=20):
        logger.info(f'Running on port {PORT}')
        await asyncio.Future()

asyncio.run(main())
