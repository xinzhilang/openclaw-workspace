#!/usr/bin/env python
"""Test version with detailed logging"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

# Force INFO level to see all our logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('OpenClaw')

RELAY_PORT = 18792
VALID_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'
connected_clients = set()

async def handle_ws(websocket, path):
    logger.info(f'WS CONNECT: {websocket.remote_address}')
    connected_clients.add(websocket)
    await websocket.send(json.dumps({'type': 'connected', 'port': RELAY_PORT}))
    try:
        async for msg in websocket:
            logger.info(f'WS MSG: {msg[:100]}')
            await websocket.send(json.dumps({'echo': msg}))
    except Exception as e:
        logger.info(f'WS CLOSED: {e}')
    finally:
        connected_clients.discard(websocket)

def process_req(path, headers):
    """This MUST return None to allow WebSocket OR (status, headers_dict, body_bytes) for HTTP"""
    logger.info(f'PROCESS_REQ: path={path!r}')
    logger.info(f'PROCESS_REQ: headers={dict(headers)}')
    
    conn = headers.get('connection', '')
    upgrade = headers.get('upgrade', '')
    
    logger.info(f'PROCESS_REQ: connection={conn!r}, upgrade={upgrade!r}')
    
    is_ws_upgrade = 'upgrade' in conn.lower() and upgrade.lower() == 'websocket'
    logger.info(f'PROCESS_REQ: is_ws_upgrade={is_ws_upgrade}')
    
    if is_ws_upgrade:
        logger.info('PROCESS_REQ: -> Returning None (allow WS upgrade)')
        return None
    
    # HTTP response
    logger.info(f'PROCESS_REQ: -> Sending HTTP response for {path}')
    if path == '/':
        body = f'<h1>OpenClaw Relay Port {RELAY_PORT}</h1><p>Clients: {len(connected_clients)}</p>'.encode()
        return (200, [('Content-Type', 'text/html'), ('Content-Length', str(len(body)))], body)
    elif path == '/status':
        body = json.dumps({'status': 'ok', 'port': RELAY_PORT}).encode()
        return (200, [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))], body)
    elif path == '/health':
        return (200, [('Content-Type', 'text/plain'), ('Content-Length', '2')], b'OK')
    
    body = b'<h1>404</h1>'
    return (404, [('Content-Type', 'text/html'), ('Content-Length', str(len(body)))], body)

async def main():
    logger.info(f'Starting on port {RELAY_PORT}')
    async with websockets.serve(
        handle_ws,
        '0.0.0.0',
        RELAY_PORT,
        process_request=process_req,
        logger=logger  # Use same logger
    ):
        logger.info('Server started!')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
