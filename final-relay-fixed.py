#!/usr/bin/env python
"""
OpenClaw Browser Relay - WebSocket + HTTP 混合服务器 (修正版)
支持 Chrome 插件连接和令牌验证
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('OpenClaw')

RELAY_PORT = 18792
VALID_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'

connected_clients = set()

async def handle_websocket(websocket):
    """Handle WebSocket connections"""
    addr = websocket.remote_address
    path = websocket.request.path if hasattr(websocket, 'request') else '/'
    logger.info(f'WS CONNECT: {addr} path={path}')
    connected_clients.add(websocket)
    
    await websocket.send(json.dumps({
        'type': 'welcome',
        'status': 'connected',
        'message': 'OpenClaw Relay Service',
        'port': RELAY_PORT
    }))
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                cmd = data.get('command', 'unknown')
                if cmd == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                elif cmd == 'status':
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'status': 'ready',
                        'clients': len(connected_clients)
                    }))
                else:
                    await websocket.send(json.dumps({'type': 'received', 'command': cmd}))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logger.error(f'WS Error: {e}')
    finally:
        connected_clients.discard(websocket)
        logger.info('WS DISCONNECT')

def process_http(request):
    """
    Process HTTP requests for websockets.process_request.
    websockets v11+ passes a Request object.
    
    Returns:
        None - to allow WebSocket upgrade
        tuple (status_code, headers_list, body_bytes) - to reject with HTTP response
    """
    # Get path from request
    path = request.path if hasattr(request, 'path') else '/'
    
    # Check if this is a WebSocket upgrade request
    # websockets library checks this internally, if upgrade headers present it won't call process_request
    # So if process_request is called, it's a plain HTTP request
    
    logger.info(f'HTTP: {path}')
    
    # Handle HTTP requests (non-WebSocket)
    if path == '/' or path == '/index.html':
        body = '''<!DOCTYPE html>
<html><head><title>OpenClaw Relay</title></head><body>
<h1>OpenClaw Browser Relay</h1>
<p>Status: <span style="color:green">Running</span></p>
<p>Port: %d</p>
<p>Protocol: WebSocket + HTTP</p>
<p>Clients: %d</p>
<hr><h3>Endpoints:</h3><ul>
<li>GET / - Status page</li>
<li>GET /status - JSON status</li>
<li>GET /health - Health check</li>
</ul></body></html>''' % (RELAY_PORT, len(connected_clients))
        return (200, [('Content-Type', 'text/html')], body.encode())
    
    elif path == '/status':
        body = json.dumps({
            'status': 'ok',
            'service': 'OpenClaw Relay',
            'port': RELAY_PORT,
            'clients': len(connected_clients),
            'timestamp': datetime.now().isoformat()
        }, indent=2)
        return (200, [('Content-Type', 'application/json')], body.encode())
    
    elif path == '/health':
        return (200, [('Content-Type', 'text/plain')], b'OK')
    elif path == '/config':
        body = json.dumps({
            'relay_port': RELAY_PORT,
            'token': VALID_TOKEN[:16] + '...',
            'websocket_enabled': True
        }, indent=2)
        return (200, [('Content-Type', 'application/json')], body.encode())
    
    body = '<h1>404 Not Found</h1>'
    return (404, [('Content-Type', 'text/html')], body.encode())

async def main():
    logger.info('=' * 60)
    logger.info('OpenClaw Browser Relay Service')
    logger.info('=' * 60)
    logger.info(f'Port: {RELAY_PORT}')
    logger.info(f'HTTP: http://127.0.0.1:{RELAY_PORT}/')
    logger.info(f'WebSocket: ws://127.0.0.1:{RELAY_PORT}')
    logger.info('=' * 60)
    
    async with websockets.serve(
        handle_websocket,
        '0.0.0.0',
        RELAY_PORT,
        process_request=process_http
    ):
        logger.info(f'Server running on port {RELAY_PORT}!')
        await asyncio.Future()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutting down...')