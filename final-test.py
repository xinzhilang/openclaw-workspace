#!/usr/bin/env python
import subprocess, time, sys, http.client, json, socket, asyncio
print('Starting relay...')
proc = subprocess.Popen([sys.executable, 'relay-service-debug.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='ignore')
time.sleep(3)

# Port check
s = socket.socket()
assert s.connect_ex(('127.0.0.1', 18792)) == 0, 'Port not open'
s.close()
print('[OK] Port 18792 open')

# HTTP tests
print('\nHTTP tests:')
for p in ['/', '/status', '/health', '/config']:
    conn = http.client.HTTPConnection('127.0.0.1', 18792, timeout=5)
    conn.request('GET', p)
    r = conn.getresponse()
    body = r.read().decode('utf-8', errors='ignore')
    conn.close()
    ok = '[OK]' if r.status == 200 else '[FAIL]'
    print('  %s %s -> %s' % (ok, p, r.status))
    if r.status == 200:
        print('    ' + body[:80])

# WebSocket test
print('\nWebSocket test:')
try:
    import websockets
    async def tw():
        async with websockets.connect('ws://127.0.0.1:18792', timeout=5) as ws:
            m = await asyncio.wait_for(ws.recv(), timeout=5)
            d = json.loads(m)
            print('  [OK] Connected, type=%s' % d.get('type'))
            await ws.send(json.dumps({'command': 'status'}))
            m2 = await asyncio.wait_for(ws.recv(), timeout=5)
            d2 = json.loads(m2)
            print('  [OK] Status: %s' % d2.get('type'))
    asyncio.run(tw())
except Exception as e:
    print('  [FAIL] %s' % e)

proc.terminate()
proc.wait(timeout=5)
print('\n[DONE]')
