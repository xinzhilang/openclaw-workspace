#!/bin/bash
# Start both servers

python -c '
import asyncio, json
from datetime import datetime

async def handle(reader, writer):
    data = await reader.read(1024)
    path = data.decode().split(" ")[1] if " " in data.decode() else "/"
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
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    else:
        response = "HTTP/1.1 200 OK\r\n\r\nOK"
    writer.write(response.encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 18792)
    async with server:
        await server.serve_forever()

asyncio.run(main())
' > /dev/null 2>&1 &
HTTP_PID=$!
echo "HTTP server started (PID: $HTTP_PID)"

sleep 2

python simple-ws-final.py > /dev/null 2>&1 &
WS_PID=$!
echo "WebSocket server started (PID: $WS_PID)"

sleep 2

echo ""
echo "Checking ports..."
python3 -c "
import socket
for port in [18792, 18793]:
    s = socket.socket()
    s.settimeout(1)
    r = s.connect_ex(('127.0.0.1', port))
    print(f'Port {port}:', 'OPEN' if r==0 else 'CLOSED')
    s.close()
" 2>&1 | grep Port

echo ""
echo "Servers are ready!"
echo "HTTP: http://127.0.0.1:18792/"
echo "WebSocket: ws://127.0.0.1:18793"
