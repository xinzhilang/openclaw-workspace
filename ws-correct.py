#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WS')

PORT = 18793

async def handler(websocket):
    """Handler - only takes websocket parameter in newer websockets"""
    addr = websocket.remote_address
    logger.info(f'Client: {addr}')
    
    # Send welcome
    await websocket.send(json.dumps({
        'type': 'welcome',
        'status': 'ok',
        'message': 'Connected to Relay'
    }))
    logger.info('Sent welcome')
    
    try:
        async for message in websocket:
            logger.info(f'Received: {message[:50]}')
            try:
                data = json.loads(message)
                if data.get('type') == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                elif data.get('type') == 'auth':
                    ok = data.get('token') == '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'
                    await websocket.send(json.dumps({'type': 'auth_result', 'success': ok}))
                else:
                    await websocket.send(json.dumps({'type': 'ack'}))
            except:
                await websocket.send(json.dumps({'type': 'error'}))
    except websockets.exceptions.ConnectionClosed:
        logger.info('Client disconnected')
    except Exception as e:
        logger.error(f'Error: {e}')

async def main():
    logger.info(f'Starting WebSocket on port {PORT}')
    async with websockets.serve(handler, '0.0.0.0', PORT, ping_interval=20):
        logger.info(f'Running on port {PORT}')
        await asyncio.Future()

asyncio.run(main())
