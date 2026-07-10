# webctrl.py — 灌肠/炮机 双模式 Web 服务（HTML 从文件加载）
import network, socket, time, json, gc
import machine
from machine import Pin, PWM

import lib.core as core

# ==================== 模式管理 ====================
_mode = 'enema'
_fucker = None
_boot_time = time.time()   # 开机时间戳

def _load_html(name):
    try:
        with open(name, 'r') as f:
            return f.read()
    except:
        return '<html><body><h1>Error loading page</h1></body></html>'

def switch_mode(m):
    global _mode, _fucker
    if m == _mode:
        return
    if m == 'fucker':
        core.safe()
        core.pump.duty(0)
        core.pump.deinit()
        gc.collect()
        from lib.fucker import Fucker
        _fucker = Fucker()
        _fucker.init()
        _mode = 'fucker'
        print('🔥 切换到炮机模式')
    elif m == 'enema':
        if _fucker:
            _fucker.deinit()
            _fucker = None
        gc.collect()
        from machine import Pin as _P, PWM as _W
        core.pump = _W(_P(19), freq=1000); core.pump.duty(0)
        _mode = 'enema'
        print('💉 切换到灌肠模式')

# ==================== HTTP ====================
def handle(cl, p):
    global _ip, _mode, _fucker
    if p == '/':
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' + _load_html('enema.html').encode())
    elif p == '/enema':
        switch_mode('enema')
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' + _load_html('enema.html').encode())
    elif p == '/fucker':
        switch_mode('fucker')
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' + _load_html('fucker.html').encode())
    elif p == '/api/status':
        d = json.dumps({'mode': _mode})
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n' + d.encode())
    elif p == '/api/mode?m=enema' or p == '/api/mode?m=fucker':
        switch_mode(p.split('=')[1])
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ip':
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n' + _ip.encode())
    elif p == '/api/q':
        hr = 0
        if core.st == core.ST_HOLD:
            hr = max(0, core.hold_set - int(time.time() - core.st_t0))
        elif core.st == core.ST_TIMED_PUMP:
            hr = max(0, core._timed_duration - int(time.time() - core.st_t0))
        alm = ""
        if core._alarm_msg and time.time() < core._alarm_until:
            alm = core._alarm_msg
        d = json.dumps({
            'ak': round(core._p_air, 1), 'wk': round(core._p_water, 1),
            'vl': round(core._vol_ml, 1), 'msg': core.msg, 'st': core.st,
            'vlv': core.rel_valve.value(), 'pmp': core.pump.duty(),
            'airp': core.rel_air.value(), 'hr': hr,
            'vt': core.vol_set, 'sp': core.spd_set,
            'at': core.air_tgt, 'wt': core.water_tgt,
            'ht': core.hold_set, 'alm': alm,
            'elapsed': int(time.time() - core.st_t0) if core.st != core.ST_IDLE else 0,
            'ads': core._ads is not None,
            'wtype': 'bridge' if hasattr(core.sensor_water, 'mv_zero') else 'hx710',
        })
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n' + d.encode())
    elif p == '/api/sys':
        import esp as _esp
        free = gc.mem_free()
        alloc = gc.mem_alloc()
        s = json.dumps({
            'mem_free': free,
            'mem_used': alloc,
            'mem_total': free + alloc,
            'cpu_freq': machine.freq(),
            'flash_size': _esp.flash_size(),
            'uptime': int(time.time() - _boot_time),
        })
        cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n' + s.encode())
    elif p == '/api/s': core.start_cycle(); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/x': core.safe(); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ion':
        core.rel_valve.value(1); time.sleep_ms(300)
        core.rel_air.value(1); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ioff': core.rel_air.value(0); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ion1':
        core.rel_valve.value(1); time.sleep_ms(300)
        core.rel_air.value(1); time.sleep_ms(500)
        core.rel_air.value(0); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ion2':
        core.rel_valve.value(1); time.sleep_ms(300)
        core.rel_air.value(1); time.sleep_ms(1000)
        core.rel_air.value(0); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ion3':
        core.rel_valve.value(1); time.sleep_ms(300)
        core.rel_air.value(1); time.sleep_ms(1500)
        core.rel_air.value(0); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/ion5':
        core.rel_valve.value(1); time.sleep_ms(300)
        core.rel_air.value(1); time.sleep_ms(2000)
        core.rel_air.value(0); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/von': core.rel_valve.value(1); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/voff': core.rel_valve.value(0); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/p10': core.timed_pump(10); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/p30': core.timed_pump(30); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/p60': core.timed_pump(60); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/pstop':
        core.pump.duty(0); core.rel_valve.value(0)
        core.st = core.ST_IDLE; core.msg = "已停止"
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/hold': core.manual_hold(); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/bz': core.buz(2); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/rst': core.flow_rst(); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/cal': core.calib(); cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p.startswith('/api/p?'):
        try:
            _, q = p.split('?', 1)
            for pair in q.split('&'):
                k, v = pair.split('=', 1); n = int(v)
                if k == 'volume': core.vol_set = max(0, min(2000, n))
                elif k == 'speed': core.spd_set = max(30, min(100, n))
                elif k == 'hold': core.hold_set = max(0, min(600, n))
                elif k == 'air_target': core.air_tgt = max(0, min(100, n))
                elif k == 'water_target': core.water_tgt = max(0, min(100, n))
        except: pass
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    # === 炮机 API ===
    elif p == '/api/f/q':
        if _fucker:
            d = json.dumps(_fucker.get_status())
            cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n' + d.encode())
        else:
            cl.send(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n{}')
    elif p == '/api/f/start':
        if _fucker: _fucker.start()
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/f/stop':
        if _fucker: _fucker.stop()
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p == '/api/f/session_90min':
        if _fucker:
            _fucker.load_session_90min()
            _fucker.mode = 6
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p.startswith('/api/f/speed?'):
        try:
            v = int(p.split('=')[1])
            if _fucker: _fucker.speed = max(0, min(100, v))
        except: pass
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p.startswith('/api/f/mode?'):
        try:
            m = int(p.split('=')[1])
            if _fucker and 0 <= m <= 6: _fucker.mode = m
        except: pass
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p.startswith('/api/f/time?'):
        try:
            t = int(p.split('=')[1])
            if _fucker: _fucker.time_limit = max(0, min(120, t))
        except: pass
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    elif p.startswith('/api/f/program?'):
        try:
            import json as _json
            _, q = p.split('?', 1)
            s = q.split('=', 1)[1]
            s = s.replace('+', ' ')
            i = 0; buf = []
            while i < len(s):
                if s[i] == '%' and i+2 < len(s):
                    buf.append(chr(int(s[i+1:i+3], 16)))
                    i += 3
                else:
                    buf.append(s[i])
                    i += 1
            stages = _json.loads(''.join(buf))
            if _fucker: _fucker.set_program(stages)
        except Exception as e:
            print(f'⚠ 节目设置失败: {e}')
        cl.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    else:
        cl.send(b'HTTP/1.0 404\r\n\r\n')

# ==================== 启动 ====================
def serve():
    global _ip
    print("=== 双模式控制器 ===")
    w = network.WLAN(network.STA_IF)
    w.active(True); w.connect("Xiaomi_6807", "guochunxi")
    t0 = time.time()
    while not w.isconnected():
        time.sleep(0.5)
        if time.time() - t0 > 15:
            print("WiFi失败"); return
    ip = w.ifconfig()[0]
    _ip = ip
    print(f"http://{ip}")
    gc.collect()
    core.disp.show_ip(ip)
    core.lcd_update()
    core.beep_startup()
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(3)
    s.settimeout(0.01)  # 10ms 超时，响应更快
    _tick_ms = time.ticks_ms()
    _req_cnt = 0
    while True:
        if time.ticks_diff(time.ticks_ms(), _tick_ms) > 50:  # 50ms 刷新传感器
            if _mode == 'fucker' and _fucker:
                _fucker.tick()
            else:
                core.tick()
            _tick_ms = time.ticks_ms()
        try:
            cl, addr = s.accept()
            try:
                r = cl.recv(1024).decode()
                p = r.split(' ')[1] if ' ' in r else '/'
                handle(cl, p)
                _req_cnt += 1
                if _req_cnt >= 10:  # 每10次请求才 GC，减少阻塞
                    gc.collect()
                    _req_cnt = 0
            except: pass
            finally:
                try: cl.close()
                except: pass
        except: pass

if __name__ == '__main__':
    serve()
