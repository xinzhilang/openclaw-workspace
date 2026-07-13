#!/usr/bin/env python3
"""
OpenClaw Browser Relay - Debug version
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('OpenClaw-Relay')

RELAY_PORT = 18792
VALID_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'

connected_clients = set()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections"""
    addr = websocket.remote_address
    logger.info(f'[INFO] WebSocket client connected: {addr}')
    connected_clients.add(websocket)
    
    await websocket.send(json.dumps({
        'type': 'welcome',
        'status': 'connected',
        'message': 'OpenClaw Relay Service'
    }))
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await websocket.send(json.dumps({'type': 'received', 'data': data}))
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)

def process_http(path, headers):
    """Process HTTP requests for websockets.process_request."""
    logger.info(f'[DEBUG] process_http called: path={path!r}')
    logger.info(f'[DEBUG] headers: {dict(headers)}')
    
    connection = headers.get('connection', '').lower()
    upgrade = headers.get('upgrade', '').lower()
    
    logger.info(f'[DEBUG] connection={connection!r}, upgrade={upgrade!r}')
    logger.info(f'[DEBUG] "upgrade" in connection: {"upgrade" in connection}')
    logger.info(f'[DEBUG] "websocket" in upgrade: {"websocket" in upgrade}')
    
    # Check if this is a WebSocket upgrade request
    if 'upgrade' in connection and 'websocket' in upgrade:
        logger.info(f'[INFO] Allowing WebSocket upgrade for path={path}')
        return None
    
    logger.info(f'[INFO] Serving HTTP response for path={path}')
    
    if path == '/' or path == '/index.html':
        body = f'<html><body><h1>OpenClaw Relay (port {RELAY_PORT})</h1></body></html>'
        return (200, [('Content-Type', 'text/html')], body.encode())
    
    elif path == '/status':
        body = json.dumps({'status': 'ok', 'port': RELAY_PORT})
        return (200, [('Content-Type', 'application/json')], body.encode())
    
    elif path == '/health':
        return (200, [('Content-Type', 'text/plain')], b'OK')
    
    body = '<h1>404 Not Found</h1>'
    return (404, [('Content-Type', 'text/html')], body.encode())

async def main():
    logger.info('='*60)
    logger.info(f'OpenClaw Browser Relay - Port {RELAY_PORT}')
    logger.info('='*60)
    
    async with websockets.serve(
        handle_websocket,
        '0.0.0.0',
        RELAY_PORT,
        process_request=process_http
    ):
        logger.info(f'Server running on port {RELAY_PORT}!')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
