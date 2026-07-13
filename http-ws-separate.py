#!/usr/bin/env python3
"""
OpenClash Relay - Separate HTTP and WebSocket servers
HTTP on port 18792, WebSocket on 18793
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('Relay')

HTTP_PORT = 18792
WS_PORT = 18793
GATEWAY_PORT = 18789
GATEWAY_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'

clients = {}

# WebSocket Server
async def ws_handler(websocket, path):
    addr = websocket.remote_address
    client_id = f'{addr[0]}:{addr[1]}'
    logger.info(f'WS Client: {client_id}')
    clients[client_id] = websocket
    
    await websocket.send(json.dumps({
        'type': 'connected',
        'service': 'OpenClash Relay',
        'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
        'token': GATEWAY_TOKEN
    }))
    
    try:
        async for msg in websocket:
            logger.info(f'Received: {msg[:50]}')
            try:
                data = json.loads(msg)
                if data.get('type') == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                elif data.get('type') == 'auth':
                    ok = data.get('token') == GATEWAY_TOKEN
                    await websocket.send(json.dumps({'type': 'auth_result', 'success': ok}))
                else:
                    await websocket.send(json.dumps({'type': 'ack'}))
            except:
                await websocket.send(json.dumps({'type': 'error', 'msg': 'invalid'}))
    except:
        pass
    finally:
        clients.pop(client_id, None)

async def start_ws_server():
    logger.info(f'WebSocket server on port {WS_PORT}')
    async with websockets.serve(ws_handler, '0.0.0.0', WS_PORT, ping_interval=20):
        await asyncio.Future()

# HTTP Server
async def handle_http(reader, writer):
    data = await reader.read(4096)
    request = data.decode()
    lines = request.split('\r\n')
    if not lines:
        writer.close()
        return
    parts = lines[0].split(' ')
    if len(parts) < 2:
        writer.close()
        return
    method = parts[0]
    path = parts[1]
    
    logger.info(f'HTTP {method} {path}')
    
    if path in ['/', '/status', '/info']:
        info = {
            'status': 'running',
            'service': 'OpenClash Browser Relay',
            'version': '1.0.0',
            'http_port': HTTP_PORT,
            'websocket_port': WS_PORT,
            'websocket': f'ws://127.0.0.1:{WS_PORT}',
            'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
            'token': GATEWAY_TOKEN,
            'gateway_token': GATEWAY_TOKEN,
            'clients': len(clients),
            'timestamp': datetime.now().isoformat()
        }
        body = json.dumps(info, ensure_ascii=False, indent=2)
        response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\n\r\n{body}'
    elif path in ['/health', '/healthcheck']:
        body = json.dumps({'status': 'healthy'})
        response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}'
    elif path in ['/token', '/gateway.token', '/gateway.auth.token']:
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(GATEWAY_TOKEN)}\r\n\r\n{GATEWAY_TOKEN}'
    else:
        body = '<h1>OpenClash Relay</h1>'
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}'
    
    writer.write(response.encode())
    await writer.drain()
    writer.close()

async def start_http_server():
    logger.info(f'HTTP server on port {HTTP_PORT}')
    server = await asyncio.start_server(handle_http, '0.0.0.0', HTTP_PORT)
    async with server:
        await server.serve_forever()

async def main():
    logger.info('='*50)
    logger.info('OpenClash Browser Relay')
    logger.info('='*50)
    logger.info(f'HTTP:  http://localhost:{HTTP_PORT}/')
    logger.info(f'WebSocket: ws://localhost:{WS_PORT}')
    logger.info(f'Gateway: ws://localhost:{GATEWAY_PORT}')
    logger.info(f'Token: {GATEWAY_TOKEN[:20]}...')
    
    # Run both servers
    await asyncio.gather(
        start_http_server(),
        start_ws_server()
    )

if __name__ == '__main__':
    asyncio.run(main())
