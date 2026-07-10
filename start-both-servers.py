#!/usr/bin/env python3
import subprocess
import sys

# Start HTTP server
http_proc = subprocess.Popen([sys.executable, '-c', """
import asyncio, json
from datetime import datetime

async def handle(reader, writer):
    data = await reader.read(1024)
    path = data.decode().split(' ')[1] if ' ' in data.decode() else '/'
    if path in ['/', '/status']:
        info = {
            'status': 'running',
            'service': 'OpenClash Browser Relay',
            'websocket_port': 18793,
            'websocket': 'ws://127.0.0.1:18793',
            'gateway': 'ws://127.0.0.1:18789',
            'token': '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a',
            'timestamp': datetime.now().isoformat()
        }
        body = json.dumps(info, ensure_ascii=False, indent=2)
        response = f'HTTP/1.1 200 OK\\r\\nContent-Type: application/json\\r\\nAccess-Control-Allow-Origin: *\\r\\nContent-Length: {len(body)}\\r\\n\\r\\n{body}'
    else:
        response = 'HTTP/1.1 200 OK\\r\\n\\r\\nOK'
    writer.write(response.encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle, '0.0.0.0', 18792)
    async with server:
        await server.serve_forever()

asyncio.run(main())
"""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print(f'Started HTTP server (PID: {http_proc.pid})')

# Start WebSocket server  
ws_proc = subprocess.Popen([sys.executable, 'simple-ws-final.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f'Started WebSocket server (PID: {ws_proc.pid})')

import time, socket
time.sleep(3)

for port in [18792, 18793]:
    s = socket.socket()
    s.settimeout(1)
    r = s.connect_ex(('127.0.0.1', port))
    print(f'Port {port}:', 'OPEN' if r==0 else 'CLOSED')
    s.close()

print('\nBoth servers are running!')
print('HTTP: http://127.0.0.1:18792/')
print('WebSocket: ws://127.0.0.1:18793')
print('\nTest with: python test-websocket.py')
"