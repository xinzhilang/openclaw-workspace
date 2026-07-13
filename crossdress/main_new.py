"""
main.py — 灌肠控制器双压力传感器

接线:
  GPIO36 — 气路传感器 (100kPa)
  GPIO39 — 水路传感器 (40kPa)
"""
from machine import ADC, Pin
import time
import urequests

# ==================== 硬件初始化 ====================
DEVICE_URL = "http://192.168.31.151/q"

air = ADC(Pin(36))
water = ADC(Pin(39))
air.atten(ADC.ATTN_11DB)
water.atten(ADC.ATTN_11DB)
air.width(ADC.WIDTH_12BIT)
water.width(ADC.WIDTH_12BIT)

# ==================== 标定参数 ====================
# 气路 (100kPa量程)  指针表标定: 0.5bar=50kPa → +0.018V
AIR_V_ZERO = 1.477
AIR_V_KPA  = 0.00036

# 水路 (40kPa量程)  指针表标定: 0.5bar=50kPa → +0.016V
WATER_V_ZERO = 1.478
WATER_V_KPA  = 0.00032

# ==================== 传感器读取 ====================
def _read_voltage(pin, samples=15):
    """多次采样取平均，返回电压值"""
    total = 0
    for _ in range(samples):
        total += pin.read()
        time.sleep_us(500)
    return total / samples / 4095 * 3.3

def read_air():
    """读取气路压力 (kPa)"""
    v = _read_voltage(air)
    return max(0, (v - AIR_V_ZERO) / AIR_V_KPA)

def read_water():
    """读取水路压力 (kPa)"""
    v = _read_voltage(water)
    return max(0, (v - WATER_V_ZERO) / WATER_V_KPA)

# ==================== 设备通讯 ====================
def fetch_device():
    """读取灌肠控制器状态"""
    try:
        r = urequests.get(DEVICE_URL, timeout=2)
        d = r.json()
        r.close()
        return d
    except Exception:
        return None

# ==================== 显示格式化 ====================
def format_output(air_kpa, water_kpa, device=None):
    parts = [f"气路:{air_kpa:5.1f}kPa  |  水路:{water_kpa:5.1f}kPa"]
    
    if device:
        ak = device.get("ak", 0)
        wk = device.get("wk", 0)
        msg = device.get("msg", "")
        parts.append(f"  |  设备:气{ak}kPa 水{wk}kPa")
        if msg:
            parts.append(f"  [{msg}]")
    
    return "".join(parts)

# ==================== 主循环 ====================
def main():
    print("=" * 50)
    print("灌肠控制器 — 双压力传感器")
    print(f"  气路: {AIR_V_KPA:.5f} kPa/V")
    print(f"  水路: {WATER_V_KPA:.5f} kPa/V")
    print("=" * 50)
    
    while True:
        akpa = read_air()
        wkpa = read_water()
        dev = fetch_device()
        print(format_output(akpa, wkpa, dev))
        time.sleep(1)

# ==================== 启动 ====================
if __name__ == "__main__":
    main()
