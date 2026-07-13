#!/usr/bin/env python3
"""
OpenClaw Browser Relay - Compatible with Shanxia Browser Relay App
Provides HTTP API + WebSocket for browser automation
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('Shanxia-Relay')

PORT = 18792
GATEWAY_PORT = 18789
GATEWAY_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'

connected_clients = {}

def create_http_response(status, content_type, body):
    """Create HTTP response"""
    if isinstance(body, dict) or isinstance(body, list):
        body = json.dumps(body, ensure_ascii=False, indent=2)
    elif isinstance(body, str):
        body = body
    else:
        body = str(body)
    
    return (
        f'HTTP/1.1 {status}\r\n'
        f'Content-Type: {content_type}\r\n'
        f'Access-Control-Allow-Origin: *\r\n'
        f'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n'
        f'Access-Control-Allow-Headers: Content-Type, Authorization\r\n'
        f'Content-Length: {len(body)}\r\n'
        f'Connection: close\r\n'
        f'\r\n'
        f'{body}'
    ).encode()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections from browser extension"""
    addr = websocket.remote_address
    client_id = f'{addr[0]}:{addr[1]}'
    logger.info(f'Client connected: {client_id}')
    connected_clients[client_id] = websocket
    
    # Send welcome message
    await websocket.send(json.dumps({
        'type': 'connected',
        'message': 'OpenClash Browser Relay',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
        'token': GATEWAY_TOKEN
    }))
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f'Message from {client_id}: {data.get("type", "unknown")}')
                
                # Handle authentication
                if data.get('type') == 'authenticate':
                    token = data.get('token', '')
                    if token == GATEWAY_TOKEN:
                        await websocket.send(json.dumps({
                            'type': 'authenticated',
                            'success': True,
                            'message': 'Token verified'
                        }))
                        logger.info(f'Client {client_id} authenticated')
                    else:
                        await websocket.send(json.dumps({
                            'type': 'authentication_failed',
                            'success': False,
                            'message': 'Invalid token'
                        }))
                
                # Handle ping
                elif data.get('type') == 'ping':
                    await websocket.send(json.dumps({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    }))
                
                # Handle status request
                elif data.get('type') == 'status':
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'success': True,
                        'data': {
                            'connected_clients': len(connected_clients),
                            'status': 'running',
                            'timestamp': datetime.now().isoformat()
                        }
                    }))
                
                # Handle gateway connection request
                elif data.get('type') == 'connect_gateway':
                    # Try to connect to gateway
                    try:
                        await websocket.send(json.dumps({
                            'type': 'gateway_connect',
                            'success': True,
                            'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
                            'message': 'Gateway connection available'
                        }))
                    except Exception as e:
                        await websocket.send(json.dumps({
                            'type': 'gateway_connect',
                            'success': False,
                            'error': str(e)
                        }))
                
                # Echo back other messages
                else:
                    await websocket.send(json.dumps({
                        'type': 'ack',
                        'success': True,
                        'received': data
                    }))
                    
            except json.JSONDecodeError:
                logger.warning(f'Invalid JSON from {client_id}')
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }))
            except Exception as e:
                logger.error(f'Error handling message: {e}')
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f'Client disconnected: {client_id}')
    except Exception as e:
        logger.error(f'Connection error: {e}')
    finally:
        connected_clients.pop(client_id, None)
        logger.info(f'Connection closed: {client_id}')

async def process_request(path, request_headers):
    """Handle HTTP requests for compatibility with Shanxia app"""
    logger.info(f'HTTP Request: {path}')
    
    # Handle preflight requests
    if path == '/favicon.ico':
        return create_http_response('404 Not Found', 'text/plain', 'Not Found')
    
    # OPTIONS request (CORS preflight)
    if request_headers.get('Origin') and 'OPTIONS' in str(request_headers):
        return create_http_response('200 OK', 'text/plain', 'OK')
    
    # Root endpoint - return relay info
    if path == '/' or path == '/status' or path == '/info':
        info = {
            'status': 'running',
            'service': 'OpenClash Browser Relay',
            'version': '1.0.0',
            'port': PORT,
            'websocket': f'ws://127.0.0.1:{PORT}',
            'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
            'token': GATEWAY_TOKEN,
            'connected_clients': len(connected_clients),
            'uptime': datetime.now().isoformat(),
            'message': 'Relay service is running and ready to accept connections'
        }
        logger.info(f'Returning status info to client')
        return create_http_response('200 OK', 'application/json', info)
    
    # Health check endpoint
    if path == '/health' or path == '/healthcheck':
        return create_http_response('200 OK', 'application/json', {
            'status': 'healthy',
            'service': 'OpenClash Browser Relay',
            'timestamp': datetime.now().isoformat()
        })
    
    # Token endpoint (for manual configuration)
    if path == '/token' or path == '/gateway.token':
        return create_http_response('200 OK', 'text/plain', GATEWAY_TOKEN)
    
    # Return 404 for other paths
    return create_http_response('404 Not Found', 'text/html', 
        '<h1>404 Not Found</h1><p>OpenClash Browser Relay Service</p>')

async def main():
    logger.info('='*60)
    logger.info('OpenClash Browser Relay Service')
    logger.info('Compatible with Shanxia Browser Relay App')
    logger.info('='*60)
    logger.info(f'Port: {PORT}')
    logger.info(f'HTTP API: http://localhost:{PORT}/')
    logger.info(f'WebSocket: ws://localhost:{PORT}')
    logger.info(f'Gateway: ws://localhost:{GATEWAY_PORT}')
    logger.info(f'Token: {GATEWAY_TOKEN[:20]}...')
    logger.info('')
    logger.info('Endpoints:')
    logger.info('  GET /          - Relay info (JSON)')
    logger.info('  GET /status    - Status info')
    logger.info('  GET /health    - Health check')
    logger.info('  GET /token     - Gateway token')
    logger.info('  WebSocket /    - WebSocket connection')
    logger.info('')
    logger.info('Waiting for connections...')
    
    # Start WebSocket server with HTTP fallback
    async with websockets.serve(
        handle_websocket,
        '0.0.0.0',
        PORT,
        process_request=process_request,
        ping_interval=20,
        ping_timeout=10,
        compression=None
    ):
        logger.info('✅ Server is running and ready!')
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('\nServer stopped by user')
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        import traceback
        traceback.print_exc()
