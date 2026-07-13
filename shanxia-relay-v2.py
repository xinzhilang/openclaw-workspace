#!/usr/bin/env python3
"""
OpenClash Browser Relay - HTTP + WebSocket
Compatible with Shanxia Browser Relay App
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('Relay')

PORT = 18792
GATEWAY_PORT = 18789
GATEWAY_TOKEN = '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a'

clients = {}

async def handler(websocket, path):
    addr = websocket.remote_address
    logger.info(f'WS Client: {addr[0]}:{addr[1]}')
    clients[addr[1]] = websocket
    
    await websocket.send(json.dumps({
        'type': 'connected',
        'message': 'OpenClash Relay',
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
                    await websocket.send(json.dumps({
                        'type': 'auth_result',
                        'success': data.get('token') == GATEWAY_TOKEN
                    }))
                else:
                    await websocket.send(json.dumps({'type': 'ack'}))
            except:
                await websocket.send(json.dumps({'type': 'echo', 'data': msg}))
    except:
        pass
    finally:
        clients.pop(addr[1], None)
        logger.info('Disconnected')

# HTTP server for API endpoints
class HTTPServer:
    def __init__(self, port):
        self.port = port
        self.token = GATEWAY_TOKEN
        
    async def handle_request(self, reader, writer):
        data = await reader.read(1024)
        request = data.decode()
        
        # Parse request line
        lines = request.split('\r\n')
        if not lines:
            writer.close()
            return
            
        request_line = lines[0]
        method_path = request_line.split(' ')
        if len(method_path) < 2:
            writer.close()
            return
            
        method = method_path[0]
        path = method_path[1]
        
        logger.info(f'HTTP {method} {path}')
        
        # Build response based on path
        if path in ['/', '/status', '/info']:
            body = json.dumps({
                'status': 'running',
                'service': 'OpenClash Browser Relay',
                'version': '1.0.0',
                'port': PORT,
                'websocket': f'ws://127.0.0.1:{PORT}',
                'gateway': f'ws://127.0.0.1:{GATEWAY_PORT}',
                'token': self.token,
                'clients': len(clients),
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\n\r\n{body}'
        
        elif path in ['/health', '/healthcheck']:
            body = json.dumps({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}'
        
        elif path in ['/token', '/gateway.token', '/gateway.auth.token']:
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(self.token)}\r\n\r\n{self.token}'
        
        else:
            body = '<h1>OpenClash Relay</h1><p>Service is running</p>'
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}'
        
        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

async def run_http_server(port):
    server = HTTPServer(port)
    srv = await asyncio.start_server(server.handle_request, '0.0.0.0', port)
    logger.info(f'HTTP Server running on port {port}')
    async with srv:
        await srv.serve_forever()

async def main():
    logger.info('='*50)
    logger.info('OpenClash Browser Relay (HTTP+WS)')
    logger.info('='*50)
    logger.info(f'HTTP: http://localhost:{PORT}')
    logger.info(f'WebSocket: ws://localhost:{PORT}')
    logger.info(f'Gateway: ws://localhost:{GATEWAY_PORT}')
    
    # Run both HTTP and WebSocket servers concurrently
    await asyncio.gather(
        run_http_server(PORT),
        websockets.serve(handler, '0.0.0.0', PORT + 1, ping_interval=20)  # WS on different port
    )

if __name__ == '__main__':
    asyncio.run(main())
