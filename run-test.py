#!/usr/bin/env python
import subprocess, time, sys, http.client, json, socket, asyncio

print("Starting relay-service.py...")
proc = subprocess.Popen(
    [sys.executable, 'relay-service.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True, errors='ignore'
)

time.sleep(4)

# Check port
sock = socket.socket()
if sock.connect_ex(('127.0.0.1', 18792)) == 0:
    print('[OK] Port 18792 is OPEN')
else:
    print('[FAIL] Port 18792 is CLOSED')
    out, _ = proc.communicate(timeout=1)
    print('Server output:', out[:500])
    sock.close()
    sys.exit(1)
sock.close()

# Test HTTP
print('\nTesting HTTP endpoints:')
for path in ['/', '/status', '/health']:
    conn = http.client.HTTPConnection('127.0.0.1', 18792, timeout=5)
    conn.request('GET', path)
    r = conn.getresponse()
    body = r.read().decode('utf-8', errors='ignore')
    conn.close()
    ok = '[OK]' if r.status == 200 else '[FAIL]'
    print('  %s %s -> %s' % (ok, path, r.status))
    if r.status == 200 and 'json' in r.getheader('Content-Type', ''):
        print('    %s' % body[:60])

# Test WebSocket
print('\nTesting WebSocket:')
try:
    import websockets
    async def test_ws():
        async with websockets.connect('ws://127.0.0.1:18792', timeout=5) as ws:
            msg = await ws.recv()
            data = json.loads(msg)
            print('  [OK] WebSocket connected, type=%s' % data.get('type'))
            return True
    asyncio.run(test_ws())
except Exception as e:
    print('  [FAIL] WebSocket: %s' % e)

proc.terminate()
proc.wait(timeout=5)
print('\n[OK] All tests complete!')
