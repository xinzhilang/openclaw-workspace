#!/usr/bin/env python3
"""
OpenClash Browser Relay - HTTP + WebSocket on same port
Compatible with Shanxia Browser Relay App
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('Relay')

PORT = 18792
GATEWAY_PORT = 18789
GATEWAY_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'

clients = {}

async def handler(websocket, path):
    """Handle WebSocket connections"""
    addr = websocket.remote_address
    client_id = f'{addr[0]}:{addr[1]}'
    logger.info(f'WS Client: {client_id}')
    clients[client_id] = websocket
    
    # Send welcome
    await websocket.send(json.dumps({
        'type': 'connected',
        'service': 'OpenClash Browser Relay',
        'version': '1.0.0',
        'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
        'token': GATEWAY_TOKEN,
        'timestamp': datetime.now().isoformat()
    }))
    
    try:
        async for message in websocket:
            logger.info(f'Message: {message[:80]}')
            try:
                data = json.loads(message)
                msg_type = data.get('type', 'unknown')
                
                if msg_type == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                elif msg_type == 'auth':
                    success = data.get('token') == GATEWAY_TOKEN
                    await websocket.send(json.dumps({
                        'type': 'auth_result',
                        'success': success,
                        'token': GATEWAY_TOKEN if success else None
                    }))
                elif msg_type == 'status':
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'status': 'running',
                        'clients': len(clients)
                    }))
                elif msg_type == 'get_token':
                    await websocket.send(json.dumps({
                        'type': 'token',
                        'token': GATEWAY_TOKEN
                    }))
                else:
                    await websocket.send(json.dumps({
                        'type': 'ack',
                        'received': msg_type
                    }))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON'
                }))
            except Exception as e:
                logger.error(f'Error: {e}')
    except:
        pass
    finally:
        clients.pop(client_id, None)
        logger.info(f'Disconnected: {client_id}')

async def http_handler(path, request_headers):
    """Handle HTTP requests - returns JSON for API endpoints"""
    logger.info(f'HTTP: {path}')
    
    # WebSocket upgrade path
    if path == '/ws':
        return None  # Let websockets library handle upgrade
    
    # Return None for root path - websockets will handle WebSocket upgrade
    # But we need to provide HTTP response for non-WebSocket clients
    if path == '/' or path == '' or path == '/status' or path == '/info':
        info = {
            'status': 'running',
            'service': 'OpenClash Browser Relay',
            'version': '1.0.0',
            'port': PORT,
            'websocket': f'ws://127.0.0.1:{PORT}',
            'ws_endpoint': f'ws://127.0.0.1:{PORT}/ws',
            'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
            'token': GATEWAY_TOKEN,
            'gateway_token': GATEWAY_TOKEN,
            'clients': len(clients),
            'timestamp': datetime.now().isoformat(),
            'message': 'Relay service is running. Connect via WebSocket.'
        }
        body = json.dumps(info, ensure_ascii=False, indent=2)
        return (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: application/json\r\n'
            b'Access-Control-Allow-Origin: *\r\n'
            b'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n'
            b'Content-Length: ' + str(len(body)).encode() + b'\r\n'
            b'\r\n'
            + body.encode()
        )
    
    # Health check
    if path in ['/health', '/healthcheck', '/ping']:
        body = json.dumps({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        return (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: application/json\r\n'
            b'Content-Length: ' + str(len(body)).encode() + b'\r\n'
            b'\r\n'
            + body.encode()
        )
    
    # Token endpoint
    if path in ['/token', '/gateway.token', '/gateway.auth.token']:
        return (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/plain\r\n'
            b'Access-Control-Allow-Origin: *\r\n'
            b'Content-Length: ' + str(len(GATEWAY_TOKEN)).encode() + b'\r\n'
            b'\r\n'
            + GATEWAY_TOKEN.encode()
        )
    
    # Default: redirect to status
    if path == '/':
        return None  # Let websockets handle
    
    # 404
    body = '<h1>404 Not Found</h1><p>OpenClash Browser Relay</p>'
    return (
        b'HTTP/1.1 404 Not Found\r\n'
        b'Content-Type: text/html\r\n'
        b'Content-Length: ' + str(len(body)).encode() + b'\r\n'
        b'\r\n'
        + body.encode()
    )

async def main():
    logger.info('='*60)
    logger.info('OpenClash Browser Relay Service')
    logger.info('HTTP + WebSocket (Compatible with Shanxia App)')
    logger.info('='*60)
    logger.info(f'Port: {PORT}')
    logger.info(f'HTTP API: http://localhost:{PORT}/')
    logger.info(f'WebSocket: ws://localhost:{PORT}/ws')
    logger.info(f'Gateway: ws://localhost:{GATEWAY_PORT}')
    logger.info(f'Token: {GATEWAY_TOKEN[:20]}...')
    logger.info('')
    logger.info('Endpoints:')
    logger.info('  GET /          - Relay status (JSON)')
    logger.info('  GET /status    - Status info')
    logger.info('  GET /health    - Health check')
    logger.info('  GET /token     - Gateway token')
    logger.info('  WS  /ws        - WebSocket connection')
    logger.info('')
    logger.info('Waiting for connections...')
    
    async with websockets.serve(
        handler,
        '0.0.0.0',
        PORT,
        process_request=http_handler,
        ping_interval=20,
        ping_timeout=10
    ):
        logger.info('✅ Server is running!')
        await asyncio.Future()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('\nServer stopped')
    except Exception as e:
        logger.error(f'Error: {e}')
        import traceback
        traceback.print_exc()
