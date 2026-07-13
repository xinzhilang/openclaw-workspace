#!/usr/bin/env python
import subprocess, time, sys, http.client, json

print("Starting relay-service.py...")
proc = subprocess.Popen(
    [sys.executable, 'relay-service.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True, errors='ignore'
)

time.sleep(4)

# Check if it's running
import socket
sock = socket.socket()
if sock.connect_ex(('127.0.0.1', 18792)) == 0:
    print('✓ Port 18792 is OPEN')
else:
    print('✗ Port 18792 is CLOSED')
    # Print server output
    out, _ = proc.communicate(timeout=1)
    print('Server output:')
    print(out[:500])
    sock.close()
    sys.exit(1)
sock.close()

# Test HTTP endpoints
print('\nTesting HTTP endpoints:')
for path in ['/', '/status', '/health', '/config']:
    try:
        conn = http.client.HTTPConnection('127.0.0.1', 18792, timeout=5)
        conn.request('GET', path)
        r = conn.getresponse()
        body = r.read().decode('utf-8', errors='ignore')
        conn.close()
        status = '✓' if r.status == 200 else '✗'
        print(f'  {status} {path} -> {r.status}')
        if r.status == 200 and 'json' in r.getheader('Content-Type', ''):
            print(f'    {body[:60]}')
    except Exception as e:
        print(f'  ✗ {path} -> ERROR: {e}')

# Test WebSocket (try a simple connection)
print('\nTesting WebSocket connection:')
try:
    import websockets
    async def test_ws():
        async with websockets.connect('ws://127.0.0.1:18792', timeout=5) as ws:
            msg = await ws.recv()
            data = json.loads(msg)
            print(f'  ✓ WebSocket connected, got: {data.get("type")}')
            return True
    asyncio.run(test_ws())
except Exception as e:
    print(f'  ✗ WebSocket: {e}')

proc.terminate()
proc.wait(timeout=5)
print('\n✓ All tests complete!')
