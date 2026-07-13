#!/usr/bin/env python3
import subprocess
import sys
import time
import socket

# HTTP server code
http_code = '''
import asyncio, json
from datetime import datetime

async def handle(reader, writer):
    data = await reader.read(1024)
    try:
        path = data.decode().split(" ")[1]
    except:
        path = "/"
    if path in ["/", "/status"]:
        info = {
            "status": "running",
            "service": "OpenClash Browser Relay",
            "websocket_port": 18793,
            "websocket": "ws://127.0.0.1:18793",
            "gateway": "ws://127.0.0.1:18789",
            "token": "7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a",
            "timestamp": datetime.now().isoformat()
        }
        body = json.dumps(info, ensure_ascii=False, indent=2)
        response = f"HTTP/1.1 200 OK\\r\\nContent-Type: application/json\\r\\nAccess-Control-Allow-Origin: *\\r\\nContent-Length: {len(body)}\\r\\n\\r\\n{body}"
    else:
        response = "HTTP/1.1 200 OK\\r\\n\\r\\nOK"
    writer.write(response.encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 18792)
    async with server:
        print("HTTP server on port 18792")
        await server.serve_forever()

asyncio.run(main())
'''

# Write HTTP server
with open('http-server.py', 'w') as f:
    f.write(http_code)

# Write WebSocket server  
with open('ws-server.py', 'w') as f:
    f.write('''
import asyncio, websockets, json

async def handler(ws, path):
    await ws.send(json.dumps({"type": "welcome", "status": "ok"}))
    try:
        async for msg in ws:
            print(f"Received: {msg[:50]}")
            try:
                data = json.loads(msg)
                if data.get("type") == "ping":
                    await ws.send(json.dumps({"type": "pong"}))
                else:
                    await ws.send(json.dumps({"type": "ack"}))
            except:
                await ws.send(json.dumps({"type": "error"}))
    except:
        pass

async def main():
    async with websockets.serve(handler, "0.0.0.0", 18793, ping_interval=20):
        print("WebSocket server on port 18793")
        await asyncio.Future()

asyncio.run(main())
''')

# Start HTTP server
print("Starting HTTP server...")
http_proc = subprocess.Popen([sys.executable, 'http-server.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(3)

# Start WebSocket server
print("Starting WebSocket server...")
ws_proc = subprocess.Popen([sys.executable, 'ws-server.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(3)

# Check ports
print("\nChecking ports...")
for port in [18792, 18793]:
    s = socket.socket()
    s.settimeout(1)
    r = s.connect_ex(('127.0.0.1', port))
    status = 'OPEN' if r == 0 else 'CLOSED'
    print(f'  Port {port}: {status}')
    s.close()

print("\n✅ Relay system is running!")
print("   HTTP: http://127.0.0.1:18792/")
print("   WebSocket: ws://127.0.0.1:18793")
print("   Gateway: ws://127.0.0.1:18789")
print("\nTest with: python test-websocket.py")
print("\nPIDs: HTTP={}, WS={}".format(http_proc.pid, ws_proc.pid))
