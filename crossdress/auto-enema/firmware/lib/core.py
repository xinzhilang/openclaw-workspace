"""
lib/core.py — 灌肠控制器 核心逻辑
  状态机、传感器、LCD、安全保护
  与 Web 服务分离，webctrl.py 通过 import core 访问
"""
import time
from machine import Pin, PWM, I2C

# ==================== 持久引脚引用 ====================
# 蜂鸣器 — 高阻态静音方案
# 响: 切OUT+LOW(0V) → 停: 切回IN(高阻)
_bz = None  # 动态创建，避免跨模式持有

def buz(n, t=80):
    for _ in range(n):
        Pin(18, Pin.OUT, value=0)   # OUT+LOW = 响
        time.sleep_ms(t)
        Pin(18, Pin.IN)             # 切回高阻 = 停
        time.sleep_ms(t // 2)

# ==================== 硬件 ====================
Pin(19, Pin.OUT, value=0); Pin(27, Pin.OUT, value=0)
time.sleep_ms(50)

pump = PWM(Pin(19), freq=1000); pump.duty(0)   # 蠕动泵
rel_air = Pin(27, Pin.OUT, value=0)               # 充气泵继电器
rel_valve = Pin(26, Pin.OUT, value=0)              # 电磁阀

# ==================== 共享 I2C ====================
_i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# ==================== 压力传感器 ====================
from lib.pressure import create_air_sensor, create_water_sensor, BridgeSensor
from lib import calibration as calib_persist  # 标定持久化

# 尝试自动检测并使用 ADS1115 (若存在)
try:
    from lib.ads1115 import create_default
    _ads = create_default(_i2c)
except Exception:
    _ads = None

sensor_air = create_air_sensor(_ads)

if _ads:
    # 水路使用新桥式传感器 (差分 AIN1-AIN3)
    sensor_water = BridgeSensor(_ads, mv_zero=7, mv_kpa=1.8)
    print("✅ 气路使用 ADS1115 (AIN0)")
    print("✅ 水路使用 ADS1115 (AIN1-AIN3 差分)")
else:
    # 无 ADS1115 时回退 HX710B
    sensor_water = create_water_sensor(extra_pulses=2)
    print("ℹ️ 回退: 气路GPIO36 + 水路HX710B")

# ===== 自动加载已保存的标定 =====
if calib_persist.has_calibration():
    calib_persist.auto_apply(sensor_air, sensor_water)
else:
    print("📭 无已保存标定，使用默认值")

# ==================== LCD (复用共享 I2C) ====================
import lib.display as disp
disp.set_i2c(_i2c)
disp.splash()

# ==================== 流量计 ====================
_fc = 0; _flt = 0
def _flow_isr(p):
    global _fc, _flt
    n = time.ticks_ms()
    if time.ticks_diff(n, _flt) > 2:
        _fc += 1; _flt = n
Pin(34, Pin.IN).irq(trigger=Pin.IRQ_FALLING, handler=_flow_isr)
def vol_ml(): return _fc / 1.35
def flow_rst(): global _fc; _fc = 0
flow_rst()

# ==================== 泵速控制 (按百分比) ====================
def _set_pump(pct=None):
    """按百分比设置泵速 (0-100)，pct=None 用 spd_set"""
    if pct is None:
        pct = spd_set
    duty = int(min(max(pct, 0), 100) / 100 * 1023)
    pump.duty(duty)

# ==================== 状态机 ====================
ST_IDLE, ST_INFL, ST_FILL, ST_HOLD, ST_TIMED_PUMP = range(5)
st = ST_IDLE; st_t0 = 0
vol_set = 300; spd_set = 70; hold_set = 30; air_tgt = 25; water_tgt = 25
msg = "就绪"
_timed_duration = 0
_alarm_msg = ""
_alarm_until = 0

# 传感器缓存（每个循环只读一次）
_p_air = 0.0; _p_water = 0.0; _vol_ml = 0.0; _tick_cnt = 0

# ==================== 开机自检（在各模块初始化完成后调用）====================
def beep_startup():
    """开机蜂鸣自检，在 webctrl.serve() 中 WiFi 连接后调用"""
    buz(3, 120)

# ==================== 标定 ====================
def calib():
    v0a = sensor_air.calibrate_zero()
    v0w = sensor_water.calibrate_zero()
    print(f"标定: 气路={v0a:.3f}V 水路={v0w:.0f}mV")
    # 自动保存到 flash，断电不丢
    calib_persist.auto_save(sensor_air, sensor_water)
    print("💾 标定参数已持久化!")

# ==================== 安全停止 ====================
def safe(alarm=None):
    global st, msg, _alarm_msg, _alarm_until
    pump.duty(0); rel_air.value(0); rel_valve.value(0)
    st = ST_IDLE
    if alarm:
        msg = alarm
        buz(5, 120)
        _alarm_msg = alarm
        _alarm_until = time.time() + 2
        lcd_update()
    else:
        msg = "已停止"
        lcd_update()

# ==================== LCD 刷新（用缓存值）====================
def lcd_update():
    global st, _alarm_msg, _alarm_until, _p_air, _p_water, _vol_ml
    if _alarm_msg and time.time() < _alarm_until:
        disp.message(_alarm_msg)
        return
    _alarm_msg = ""
    if st == ST_IDLE:
        disp.idle(_p_air, _p_water, _vol_ml)
    elif st == ST_INFL:
        disp.inflating(_p_air, air_tgt)
    elif st == ST_FILL:
        disp.filling(_vol_ml, vol_set, _p_water)
    elif st == ST_HOLD:
        r = max(0, hold_set - int(time.time() - st_t0))
        disp.holding(r, _p_air, _p_water)
    elif st == ST_TIMED_PUMP:
        r = max(0, _timed_duration - int(time.time() - st_t0))
        disp.timed_pump(r)
    else:
        disp.message(msg)

# ==================== 开始循环 ====================
def start_cycle():
    global st, st_t0, msg
    if st != ST_IDLE: return
    rel_valve.value(1)
    time.sleep_ms(100)
    rel_air.value(1)
    st = ST_INFL; st_t0 = time.time(); msg = "启动"
    lcd_update()

# ==================== 定时注水 ====================
def timed_pump(seconds):
    global st, st_t0, _timed_duration, msg
    if st != ST_IDLE: return
    _set_pump()
    st = ST_TIMED_PUMP; st_t0 = time.time(); _timed_duration = seconds
    msg = f"注水{seconds}s"
    lcd_update()

# ==================== 手动保持 ====================
def manual_hold():
    """手动进入保持（任意状态均可）"""
    global st, st_t0, msg
    pump.duty(0); rel_air.value(0)
    if st != ST_HOLD:
        st = ST_HOLD; st_t0 = time.time(); msg = "手动保持"
        lcd_update()

# ==================== 主状态循环 ====================
def tick():
    """主状态循环，每次循环调用"""
    global st, st_t0, msg, _p_air, _p_water, _vol_ml, _tick_cnt

    _p_air = sensor_air.read_kpa()
    _p_water = sensor_water.read_kpa()
    _vol_ml = vol_ml()

    _tick_cnt += 1
    if _tick_cnt >= 5 or st != ST_IDLE:
        lcd_update()
        _tick_cnt = 0

    if st == ST_IDLE: return
    t = time.time()

    # === ⚠ 最高优先级：过压保护 ===
    p_air = _p_air; p_water = _p_water
    ol = 50
    if air_tgt > 0 and p_air > max(air_tgt * 1.5, ol):
        safe("气压过高!"); return
    if water_tgt > 0 and p_water > max(water_tgt * 1.5, ol):
        safe("水压过高!"); return

    no_air = air_tgt <= 0
    no_water = water_tgt <= 0

    if st == ST_TIMED_PUMP:
        remain = _timed_duration - int(t - st_t0)
        if remain <= 0:
            pump.duty(0); rel_valve.value(0)
            st = ST_IDLE; msg = "注水完成"
            buz(3, 100)
            _alarm_msg = msg
            _alarm_until = time.time() + 2
        else:
            msg = f"注水中...{remain}s"
    elif st == ST_INFL:
        p = p_air
        if no_air:
            rel_air.value(0); flow_rst()
            _set_pump()
            st = ST_FILL; st_t0 = t
        else:
            msg = f"充气 {p:.0f}/{air_tgt}kPa"
            if p >= air_tgt:
                rel_air.value(0); flow_rst()
                _set_pump()
                st = ST_FILL; st_t0 = t
            elif t - st_t0 > 30: safe("充气超时")
    elif st == ST_FILL:
        m = _vol_ml; w = p_water
        msg = f"注水 {m:.0f}/{vol_set}ml"
        if not no_water and w > water_tgt: safe("水压过高!"); return
        if m >= vol_set:
            pump.duty(0)
            st = ST_HOLD; st_t0 = t
        elif t - st_t0 > 300: safe("注水超时")
    elif st == ST_HOLD:
        p = p_air; r = max(0, hold_set - int(t - st_t0))
        msg = f"保持 {r}s 气压{p:.0f}kPa"
        if not no_air and int(t - st_t0) > 2 and p < 10:
            safe("脱落!"); return
        if not no_air and p < air_tgt and p >= 10:
            rel_air.value(1); time.sleep_ms(150); rel_air.value(0)
        if r <= 0:
            msg = f"完成! {_vol_ml:.0f}ml"; st = ST_IDLE
            buz(3, 100)
            rel_valve.value(0)
            _alarm_msg = msg
            _alarm_until = time.time() + 2

    if st != ST_IDLE:
        lcd_update()
